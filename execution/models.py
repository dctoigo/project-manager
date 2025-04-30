from django.db import models

# Clients
class Client(models.Model):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Contracts
class Contract(models.Model):
    BILLING_TYPE_CHOICES = [
        ('Hourly', 'Hourly'),
        ('Fixed Price', 'Fixed Price'),
    ]

    BILLING_CADENCE_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Weekly', 'Weekly'),
        ('Fixed Date', 'Fixed Date'),
    ]

    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    contract_date = models.DateField()
    contract_value = models.DecimalField(max_digits=12, decimal_places=2)
    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES, default=None)
    billing_cadence = models.CharField(max_length=20, choices=BILLING_CADENCE_CHOICES, default=None)

    def __str__(self):
        return f"{self.name} ({self.client.name})"

# Projects
class Project(models.Model):
    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Paused', 'Paused'),
        ('Done', 'Done'),
    ]

    name = models.CharField(max_length=255)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    start_date = models.DateField()
    due_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Tasks
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Paused', 'Paused'),
        ('Done', 'Done'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    due_date = models.DateField()
    ready_to_invoice = models.BooleanField(default=False)
    invoiced = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name
    
    @property
    def total_duration_hours(self):
        sessions = self.time_sessions.filter(start_time__isnull=False, end_time__isnull=False)
        return round(sum([(s.end_time - s.start_time).total_seconds() for s in sessions]) / 3600, 2)
    
    @property
    def active_time_session(self):
        return self.time_sessions.filter(end_time__isnull=True).first()

# Invoices
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Paid', 'Paid'),
        ('Canceled', 'Canceled'),
    ]

    REVENUE_TYPE_CHOICES = [
        ('Fixed', 'Fixed'),
        ('Variable', 'Variable'),
    ]

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
            return self.contract.fixed_amount  # Presume que o contrato tem um campo fixed_amount
        return sum(session.hourly_rate * session.duration_hours for session in self.sessions.all())

# Time Sessions
class TimeSession(models.Model):
    name = models.CharField(max_length=255)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    work_description = models.TextField(blank=True, null=True)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')

    @property
    def duration_hours(self):
        if self.start_time and self.end_time:
            return round((self.end_time - self.start_time).total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"Session for {self.task.name}"

# Expenses
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Travel', 'Travel'),
        ('Hosting', 'Hosting'),
        ('Material', 'Material'),
        ('Licensing', 'Licensing'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    expense_date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.category}"