from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.executive_dashboard, name='dashboard'),

    # Clientes
    path('clients/add/', views.add_client, name='add_client'),
    path('clients/', views.list_clients, name='list_clients'),

    # Contratos
    path('contracts/add/', views.add_contract, name='add_contract'),

    # Projetos
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/', views.list_projects, name='list_projects'),

    # Tarefas
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/', views.list_tasks, name='list_tasks'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/toggle/', views.start_stop_task, name='start_stop_task'),

    # Sessões de Trabalho
    path('sessions/add/', views.add_time_session, name='add_time_session'),

    # Invoices
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/', views.list_invoices, name='list_invoices'),
    path('invoices/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('invoices/<int:invoice_id>/cancel/', views.cancel_invoice, name='cancel_invoice'),
    path('invoices/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('invoices/<int:invoice_id>/email/', views.send_invoice_email, name='send_invoice_email'),
    path('invoices/<int:invoice_id>/email-pdf/', views.send_invoice_pdf_email, name='send_invoice_pdf_email'),

    # Exportação e Painel de Tempo
    path('export/time-report/', views.export_time_report, name='export_time_report'),
    path('time-overview/', views.time_overview, name='time_overview'),
]
