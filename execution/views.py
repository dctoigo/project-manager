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

from .models import Client, Contract, Project, Task, TimeSession, Invoice, Expense
from .forms import (
    ClientForm, ContractForm, ProjectForm, TaskForm, TimeSessionForm, InvoiceForm 
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

