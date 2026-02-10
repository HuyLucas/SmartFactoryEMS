from django.db import models


class Machine(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=120)
    workshop_area = models.CharField(max_length=120)
    rated_power_kw = models.FloatField()
    installation_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    alert_threshold_kw = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.workshop_area})"


class EnergyRecord(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='energy_records')
    voltage = models.FloatField()
    current = models.FloatField()
    power_kw = models.FloatField()
    energy_kwh = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.machine.name} @ {self.timestamp}"


class Alert(models.Model):
    ALERT_LEVELS = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='alerts')
    message = models.TextField()
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVELS)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.machine.name} - {self.alert_level}"
