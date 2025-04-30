from django.db import models
from django.utils import timezone

# Clientes
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

# Contratos
class Contract(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    revenue_type = models.CharField(max_length=20, choices=[('Fixed', 'Fixed'), ('Variable', 'Variable')])
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_frequency = models.CharField(max_length=50, choices=[
        ('One-time', 'One-time'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('On Completion', 'On Completion')
    ])

    def __str__(self):
        return f"{self.client.name} - {self.revenue_type}"

# Projetos
class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Tarefas
class Task(models.Model):
    STATUS_CHOICES = [('To Do', 'To Do'), ('In Progress', 'In Progress'), ('Done', 'Done')]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    priority = models.CharField(max_length=20)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')

    def __str__(self):
        return self.name

    @property
    def active_time_session(self):
        return self.time_sessions.filter(end_time__isnull=True).first()

    @property
    def total_duration_hours(self):
        sessions = self.time_sessions.filter(start_time__isnull=False, end_time__isnull=False)
        return round(sum([(s.end_time - s.start_time).total_seconds() for s in sessions]) / 3600, 2)

# Invoices
class Invoice(models.Model):
    STATUS_CHOICES = [('Draft', 'Draft'), ('Sent', 'Sent'), ('Paid', 'Paid'), ('Canceled', 'Canceled')]
    REVENUE_TYPE_CHOICES = [('Fixed', 'Fixed'), ('Variable', 'Variable')]

    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    tasks = models.ManyToManyField(Task, blank=True)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    def __str__(self):
        return f"Invoice {self.invoice_number or self.pk} - {self.client.name}"

    @property
    def total_hours(self):
        return sum(
            (session.end_time - session.start_time).total_seconds()
            for session in self.sessions.all()
            if session.end_time and session.start_time
        ) / 3600

    @property
    def total_amount(self):
        if self.revenue_type == 'Fixed':
            return self.contract.fixed_amount or 0
        return sum(session.hourly_rate * session.duration_hours for session in self.sessions.all())

# Sessões de Trabalho
class TimeSession(models.Model):
    task = models.ForeignKey(Task, related_name='time_sessions', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')

    def __str__(self):
        return self.name or f"Session {self.pk}"

    @property
    def duration_hours(self):
        if self.start_time and self.end_time:
            return round((self.end_time - self.start_time).total_seconds() / 3600, 2)
        return 0
