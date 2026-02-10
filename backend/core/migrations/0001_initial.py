from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('workshop_area', models.CharField(max_length=120)),
                ('rated_power_kw', models.FloatField()),
                ('installation_date', models.DateField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('alert_threshold_kw', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='EnergyRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voltage', models.FloatField()),
                ('current', models.FloatField()),
                ('power_kw', models.FloatField()),
                ('energy_kwh', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='energy_records', to='core.machine')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('alert_level', models.CharField(choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('CRITICAL', 'Critical')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('acknowledged', models.BooleanField(default=False)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='core.machine')),
            ],
        ),
    ]
