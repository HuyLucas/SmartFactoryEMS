from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from core.models import Machine
from datetime import date


class Command(BaseCommand):
    help = 'Create demo users, groups, and sample machines.'

    def handle(self, *args, **options):
        for group_name in ['Admin', 'Engineer', 'Operator']:
            Group.objects.get_or_create(name=group_name)

        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser('admin', 'admin@example.com', 'Admin123!')
            user.groups.add(Group.objects.get(name='Admin'))
            self.stdout.write(self.style.SUCCESS('Created admin user (admin/Admin123!).'))

        if not User.objects.filter(username='engineer').exists():
            user = User.objects.create_user('engineer', 'engineer@example.com', 'Engineer123!')
            user.groups.add(Group.objects.get(name='Engineer'))
            self.stdout.write(self.style.SUCCESS('Created engineer user (engineer/Engineer123!).'))

        if not User.objects.filter(username='operator').exists():
            user = User.objects.create_user('operator', 'operator@example.com', 'Operator123!')
            user.groups.add(Group.objects.get(name='Operator'))
            self.stdout.write(self.style.SUCCESS('Created operator user (operator/Operator123!).'))

        if Machine.objects.count() == 0:
            Machine.objects.bulk_create([
                Machine(
                    name='CNC Lathe #1',
                    workshop_area='Machining',
                    rated_power_kw=6.5,
                    installation_date=date(2021, 6, 1),
                    status='active',
                    alert_threshold_kw=7.5,
                ),
                Machine(
                    name='Hydraulic Press',
                    workshop_area='Fabrication',
                    rated_power_kw=8.0,
                    installation_date=date(2020, 9, 12),
                    status='active',
                    alert_threshold_kw=8.8,
                ),
                Machine(
                    name='Welding Station A',
                    workshop_area='Welding',
                    rated_power_kw=4.0,
                    installation_date=date(2022, 1, 5),
                    status='active',
                    alert_threshold_kw=4.8,
                ),
                Machine(
                    name='Paint Booth',
                    workshop_area='Finishing',
                    rated_power_kw=5.0,
                    installation_date=date(2021, 3, 20),
                    status='inactive',
                    alert_threshold_kw=6.0,
                ),
            ])
            self.stdout.write(self.style.SUCCESS('Seeded sample machines.'))
