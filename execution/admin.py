from django.contrib import admin
from .models import Client, Contract, Project, Task, TimeSession, Invoice, Expense

# TimeSession Inline para aparecer dentro da Task
class TimeSessionInline(admin.TabularInline):
    model = TimeSession
    extra = 1  # Quantos novos registros aparecem inicialmente
    fields = ('name', 'start_time', 'end_time', 'work_description')
    readonly_fields = ('duration_hours',)

# Task Inline para aparecer dentro da Invoice (opcional)
class TaskInline(admin.TabularInline):
    model = Invoice.tasks.through  # Como é ManyToMany
    extra = 1

# Clients
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'contact_info')
    search_fields = ('name', 'company', 'contact_info')

# Contracts
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'contract_date', 'contract_value', 'billing_type', 'billing_cadence')
    list_filter = ('billing_type', 'billing_cadence', 'contract_date')
    search_fields = ('name', 'client__name')

# Projects
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'contract', 'status', 'start_date', 'due_date')
    list_filter = ('status', 'start_date', 'due_date')
    search_fields = ('name', 'client__name', 'contract__name')

# Tasks
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'client', 'priority', 'status', 'due_date', 'amount', 'ready_to_invoice', 'invoiced')
    list_filter = ('priority', 'status', 'ready_to_invoice', 'invoiced')
    search_fields = ('name', 'project__name', 'client__name')
    inlines = [TimeSessionInline]

# TimeSessions
@admin.register(TimeSession)
class TimeSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'task', 'start_time', 'end_time', 'duration_hours')
    search_fields = ('name', 'task__name')
    readonly_fields = ('duration_hours',)

    @admin.display(description='Duration (h)')
    def duration(self, obj):
        return obj.duration_hours

# Invoices
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'contract', 'invoice_date', 'due_date', 'status', 'revenue_type', 'total_amount_display')
    list_filter = ('status', 'revenue_type', 'invoice_date')
    search_fields = ('invoice_number', 'client__name', 'contract__name')
    inlines = [TaskInline]

    def total_amount_display(self, obj):
        return f"${obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount'

# Expenses
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'client', 'expense_date', 'category', 'amount')
    list_filter = ('category', 'expense_date')
    search_fields = ('name', 'project__name', 'client__name')