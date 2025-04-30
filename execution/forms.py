
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from .models import Client, Contract, Project, Task, TimeSession, Invoice, Expense

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name',
            'company',
            'cnpj',
            'contact_name',
            'contact_info',
            'phone',
            'contact_phone',
            'email',
            'contact_email',
            'email_invoice',
            'website',
            'address',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name'), Column('company'), css_class="g-3"),
            Row(Column('cnpj'), Column('website'), css_class="g-3"),

            Row(Column('contact_name'), Column('contact_info'), css_class="g-3"),
            Row(Column('phone'), Column('contact_phone'), css_class="g-3"),

            Row(Column('email'), Column('contact_email'), css_class="g-3"),
            Row(Column('email_invoice'), css_class="g-3"),

            Row(Column('address', css_class="col-12")),
            Row(Column('notes', css_class="col-12")),
        )

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

class TimeSessionForm(forms.ModelForm):
    class Meta:
        model = TimeSession
        fields = '__all__'
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'contract', 'due_date', 'revenue_type', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'project', 'contract', 'client', 'expense_date', 'category', 'amount', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'contract': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.input_type == 'checkbox':
                field.widget.attrs['class'] = 'form-check-input'
            elif field.widget.input_type == 'select':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
