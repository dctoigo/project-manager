from django.shortcuts import render
from django.db.models import Sum, Q, F
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404 as get_404
from django.http import HttpResponse
from django.db.models.functions import TruncDate
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Client, Contract, Project, Task, TimeSession, Invoice, Expense
from .forms import (
    ClientForm, ContractForm, ProjectForm, TaskForm, TimeSessionForm, InvoiceForm, ExpenseForm
)

from io import BytesIO
from datetime import timedelta, date
from xhtml2pdf import pisa

import csv

# Create your views here.

# Base View to handle form submissions
def handle_form(request, form_class, template_name, page_tittle, button_text, success_message):
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, template_name, {
        'form': form,
        'page_title': page_tittle,
        'button_text': button_text
    })

# Executive Dashboard View
@login_required
def executive_dashboard(request):
    total_revenue = Invoice.objects.filter(status='Paid').aggregate(total=Sum('tasks__amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_profit = total_revenue - total_expenses

    pending_invoices = Invoice.objects.filter(status__in=['Draft', 'Sent']).count()
    paid_invoices = Invoice.objects.filter(status='Paid').count()

    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices,
    }
    return render(request, 'execution/executive_dashboard.html', context)


# Cadastrar Tarefa

def add_task(request, project_id=None, client_id=None):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task created successfully!')
            return redirect('dashboard')
    else:
        form = TaskForm()
        if project_id:
            form.fields['project'].initial = project_id
        if client_id:
            form.fields['client'].initial = client_id

    context = {
        'form': form,
        'page_title': 'Add New Task',
        'button_text': 'Add Task'
    }

    return render(request, 'execution/interaction.html', context)

# Listar Tarefas
def list_tasks(request):
    clients = Client.objects.prefetch_related('project_set__task_set')
    status_filter = request.GET.get('status')

    if status_filter:
        for client in clients:
            client.filtered_projects = []
            for project in client.project_set.all():
                project.filtered_tasks = project.task_set.filter(status=status_filter)
                if project.filtered_tasks.exists():
                    client.filtered_projects.append(project)
    else:
        for client in clients:
            client.filtered_projects = client.project_set.all()

    return render(request, 'execution/list_tasks.html', {
        'clients': clients,
        'page_title': 'Tasks by Client'
    })

# Editar Tarefa
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('list_tasks')
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'page_title': 'Edit Task',
        'button_text': 'Update Task'
    }

    return render(request, 'execution/interaction.html', context)

# Deletar Tarefa
def delete_task(request, task_id):
    task = get_404(Task.objects.get(id=task_id))

    if request.method == 'POST':
        if task.time_sessions.exists():
            messages.error(request, 'Task cannot be deleted while there are time sessions associated with it.')
            return redirect('list_tasks')
        
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('list_tasks')

# Completar Tarefa
def complete_task(request, task_id):
    task = get_404(Task, id=task_id)

    has_open_session = task.time_sessions.filter(end_time__isnull=True).exists()
    if has_open_session:
        messages.error(request, 'Task cannot be marked as completed while there are open time sessions.')
        return redirect('list_tasks')
    else:
        task.status = 'Done'
        task.save()
        messages.success(request, 'Task marked as completed!')
    return redirect('list_tasks')

# Cadastrar Sessão de Trabalho
def add_time_session(request):
    return handle_form(request, TimeSessionForm, 'execution/interaction.html', 'Add New Time Session', 'Add Time Session', 'Time Session created successfully!')

# Iniciar/Parar Sessão de Trabalho
def start_stop_task(request, task_id):
    task = get_404(Task.objects.get(id=task_id))

    if task.status == 'Done':
        messages.error(request, 'Can`t start a task that is already completed.')
        return redirect('list_tasks')
    
    open_session = task.time_sessions.filter(end_time__isnull=True).first()
    if open_session:
        open_session.end_time = timezone.now()
        open_session.save()
        messages.success(request, 'Time Session stopped for task!')
    else:
        task.time_sessions.create(
            name=f"Session {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            start_time=timezone.now(),
        )
        if task.status != 'In Progress':
            task.status = 'In Progress'
            task.save()    
        messages.success(request, 'Time Session started for task!')
    
    return redirect('list_tasks')

# Exportar Relatório de Horas
def export_time_report(request):
    tasks = Task.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="time_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Task', 'Project', 'Client', 'Status', 'Hours Spent'])

    for task in tasks:
        writer.writerow([
            task.name,
            task.project.name if task.project else '',
            task.client.name if task.client else '',
            task.status,
            task.total_duration_hours
        ])

    return response

# Time Overview
def time_overview(request):
    start = date.today() - timedelta(days=180)  # últimos 6 meses
    sessions = (
        TimeSession.objects
        .filter(start_time__date__gte=start)
        .annotate(day=TruncDate('start_time'))
        .values('day')
        .annotate(total_hours=Sum(
            (F('end_time') - F('start_time'))
        ))
    )

    # Converte para dicionário {data: horas}
    heatmap_data = {}
    for s in sessions:
        if s['total_hours']:
            total_seconds = s['total_hours'].total_seconds()
            heatmap_data[s['day']] = round(total_seconds / 3600, 2)

    return render(request, 'execution/time_overview.html', {
        'heatmap_data': heatmap_data
    })

# Cadastrar Cliente
def add_client(request):
    return handle_form(request, ClientForm, 'execution/add_client.html', 'Add New Client', 'Add Client', 'Client created successfully!')

# Listar Clientes
def list_clients(request):
    clients = Client.objects.all()
    context = {
        'clients': clients,
        'page_title': 'List of Clients'
    }
    return render(request, 'execution/list_clients.html', context)

# Cadastrar Contrato
def add_contract(request):
    return handle_form(request, ContractForm, 'execution/interaction.html', 'Add New Contract', 'Add Contract', 'Contract created successfully!')

# Cadastrar Projeto
def add_project(request):
    return handle_form(request, ProjectForm, 'execution/interaction.html', 'Add New Project', 'Add Project', 'Project created successfully!')

# Listar Projetos
def list_projects(request):
    projects = Project.objects.select_related('client').prefetch_related('task_set')
    return render(request, 'execution/list_projects.html', {
        'projects': projects,
        'page_title': 'Project List'
    })

# Cadastrar Fatura
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        session_ids = request.POST.getlist('sessions')
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.invoice_number = f"INV-{Invoice.objects.count() + 1:04d}"
            invoice.save()
            form.save_m2m()

            # Associar sessões
            TimeSession.objects.filter(id__in=session_ids).update(invoice=invoice)

            # Associar tasks envolvidas
            invoice.tasks.set(Task.objects.filter(time_sessions__invoice=invoice).distinct())

            return redirect('view_invoice', invoice.id)
    else:
        form = InvoiceForm()

    sessions = TimeSession.objects.filter(end_time__isnull=False, invoice__isnull=True)
    return render(request, 'execution/add_invoice.html', {
        'form': form,
        'sessions': sessions
    })

# Visualizar Fatura
def view_invoice(request, invoice_id):
    invoice = get_404(Invoice, id=invoice_id)
    return render(request, 'execution/view_invoice.html', {'invoice': invoice})

# Cancelar Fatura
def cancel_invoice(request, invoice_id):
    invoice = get_404(Invoice, id=invoice_id)
    invoice.sessions.update(invoice=None)
    invoice.status = 'Canceled'
    invoice.save()
    return redirect('view_invoice', invoice.id)

# Listar Faturas
def list_invoices(request):
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = Invoice.objects.filter(status=status_filter)
    else:
        invoices = Invoice.objects.all()
    
    context = {
        'invoices': invoices,
        'page_title': 'Invoices'
    }

    return render(request, 'execution/list_invoices.html', context)

# Gerar PDF da Fatura
def generate_invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    template = get_template('execution/invoice_print.html')
    html = template.render({'invoice': invoice})

    result = BytesIO()
    pdf_status = pisa.CreatePDF(src=html, dest=result)

    if not pdf_status.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{invoice.invoice_number or invoice.id}.pdf"'
        return response
    return HttpResponse('Error generating PDF', status=500)

# Enviar E-mail da Fatura
def send_invoice_pdf_email(request, invoice_id):
    invoice = get_404(Invoice, id=invoice_id)
    client = invoice.client

    # 🔒 Check: email de envio
    if not client.email_invoice:
        messages.error(request, "Client does not have an email_invoice configured.")
        return redirect('view_invoice', invoice_id)

    # Renderiza HTML
    template = get_template('execution/invoice_print.html')
    html = template.render({'invoice': invoice})

    # Gera PDF em memória
    pdf_file = BytesIO()
    pdf_status = pisa.CreatePDF(src=html, dest=pdf_file)

    if pdf_status.err:
        messages.error(request, "Error generating PDF.")
        return redirect('view_invoice', invoice_id)

    # Monta e envia e-mail
    email = EmailMessage(
        subject=f"Invoice {invoice.invoice_number}",
        body="Please find attached your invoice.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[client.email_invoice],
        cc=[client.contact_email] if client.contact_email else None,
    )
    email.attach(
        filename=f"invoice_{invoice.invoice_number or invoice.id}.pdf",
        content=pdf_file.getvalue(),
        mimetype="application/pdf"
    )
    email.send()

    messages.success(request, "Invoice sent successfully.")
    return redirect('view_invoice', invoice_id)

# Enviar E-mail da Fatura (sem PDF)
def send_invoice_email(request, invoice_id):
    invoice = get_404(Invoice, id=invoice_id)
    client = invoice.client

    # Verificação obrigatória
    if not client.email_invoice:
        messages.error(request, "Client does not have an 'email_invoice' configured.")
        return redirect('view_invoice', invoice_id)

    subject = f"Invoice {invoice.invoice_number or invoice.id}"
    html_content = render_to_string('execution/email_invoice.html', {'invoice': invoice})

    try:
        send_mail(
            subject=subject,
            message='',  # plaintext vazio
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email_invoice],
            cc=[client.contact_email] if client.contact_email else None,
            fail_silently=False,
        )
        messages.success(request, "Invoice email sent successfully.")
    except Exception as e:
        messages.error(request, f"Error sending email: {str(e)}")

    return redirect('view_invoice', invoice_id)

# Cadastrar Despesa
def add_expense(request):
    
    return handle_form(request, ExpenseForm, 'execution/interaction.html', 'Add New Expense', 'Add Expense', 'Expense created successfully!')

# User Profile
@login_required
def user_profile(request):
    return render(request, 'profile.html')