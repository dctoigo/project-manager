
from django.contrib import admin
from .models import Client, Contract, Project, Task, TimeSession, Invoice

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('client', 'revenue_type', 'billing_frequency', 'fixed_amount')
    list_filter = ('revenue_type', 'billing_frequency')
    search_fields = ('client__name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client')
    search_fields = ('name', 'client__name')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'client', 'status', 'due_date')
    list_filter = ('status', 'priority')
    search_fields = ('name', 'project__name', 'client__name')

@admin.register(TimeSession)
class TimeSessionAdmin(admin.ModelAdmin):
    list_display = ('task', 'start_time', 'end_time', 'hourly_rate', 'invoice')
    list_filter = ('invoice',)
    search_fields = ('task__name',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'status', 'invoice_date', 'due_date', 'revenue_type')
    list_filter = ('status', 'revenue_type')
    search_fields = ('invoice_number', 'client__name')
