from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('/', views.executive_dashboard, name='dashboard'),
    path('dashboard/', views.executive_dashboard, name='dashboard'),

    # Formularios
    path('add-client/', views.add_client, name='add_client'),
    path('add-contract/', views.add_contract, name='add_contract'),
    path('add-project/', views.add_project, name='add_project'),
    path('add-task/', views.add_task, name='add_task'),
    path('add-task/<int:project_id>/<int:client_id>/',views.add_task, name='add_task_with_project'),
    
    path('add-time-session/', views.add_time_session, name='add_time_session'),
    path('add-invoice/', views.add_invoice, name='add_invoice'),
    path('add-expense/', views.add_expense, name='add_expense'),

    # Listagens
    path('list-clients/', views.list_clients, name='list_clients'),
    path('list-tasks/', views.list_tasks, name='list_tasks'),
    path('list-projects/', views.list_projects, name='list_projects'),

    # Tasks Actons
    path('task/complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('task/start-stop/<int:task_id>/', views.start_stop_task, name='start_stop_task'),
    path('task/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),

    # Invoices
    path('invoices/add/', views.add_invoice, name='add_invoice'),
    path('invoices/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('invoices/<int:invoice_id>/cancel/', views.cancel_invoice, name='cancel_invoice'),
    path('invoices/', views.list_invoices, name='list_invoices'),
    path('invoices/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('invoices/<int:invoice_id>/email/', views.send_invoice_email, name='send_invoice_email'),
    path('invoices/<int:invoice_id>/email-pdf/', views.send_invoice_pdf_email, name='send_invoice_pdf_email'),
    path('invoices/<int:invoice_id>/cancel/', views.cancel_invoice, name='cancel_invoice'),

    # Other Functions
    path('export-time-report/', views.export_time_report, name='export_time_report'),
    path('time-overview/', views.time_overview, name='time_overview')
]