
from django import forms
from .models import Client, Contract, Project, Task, TimeSession, Invoice

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

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
