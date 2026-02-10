from datetime import datetime, timedelta
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import Machine, EnergyRecord, Alert
from .serializers import MachineSerializer, EnergyRecordSerializer, AlertSerializer
from .permissions import IsAdminOrEngineer


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all().order_by('name')
    serializer_class = MachineSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrEngineer()]
        return [IsAuthenticated()]


class EnergyRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EnergyRecord.objects.select_related('machine').all().order_by('-timestamp')
    serializer_class = EnergyRecordSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['timestamp', 'power_kw']


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('machine').all().order_by('-created_at')
    serializer_class = AlertSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrEngineer()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.acknowledged = True
        alert.save(update_fields=['acknowledged'])
        return Response(self.get_serializer(alert).data)


class EnergyIngestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required_fields = ['machine_id', 'voltage', 'current', 'power_kw', 'energy_kwh']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'Missing field {field}'}, status=status.HTTP_400_BAD_REQUEST)

        machine = Machine.objects.get(id=data['machine_id'])
        record = EnergyRecord.objects.create(
            machine=machine,
            voltage=data['voltage'],
            current=data['current'],
            power_kw=data['power_kw'],
            energy_kwh=data['energy_kwh'],
        )

        alert_payload = None
        if record.power_kw > machine.alert_threshold_kw:
            alert = Alert.objects.create(
                machine=machine,
                message=(
                    f"Power draw {record.power_kw:.2f} kW exceeds threshold "
                    f"{machine.alert_threshold_kw:.2f} kW"
                ),
                alert_level='CRITICAL',
            )
            alert_payload = AlertSerializer(alert).data

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'energy_updates',
            {
                'type': 'energy.update',
                'payload': {
                    'record': EnergyRecordSerializer(record).data,
                    'alert': alert_payload,
                },
            },
        )

        return Response(EnergyRecordSerializer(record).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    total_power = EnergyRecord.objects.aggregate(total=Sum('power_kw'))['total'] or 0
    workshop_breakdown = (
        EnergyRecord.objects.values('machine__workshop_area')
        .annotate(total=Sum('power_kw'))
        .order_by('-total')
    )
    top_machines = (
        EnergyRecord.objects.values('machine__name')
        .annotate(total=Sum('power_kw'))
        .order_by('-total')[:5]
    )
    latest_alerts = Alert.objects.select_related('machine').order_by('-created_at')[:10]

    return Response({
        'total_power_kw': total_power,
        'workshop_breakdown': list(workshop_breakdown),
        'top_machines': list(top_machines),
        'alerts': AlertSerializer(latest_alerts, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_daily(request):
    start = datetime.utcnow() - timedelta(days=1)
    records = EnergyRecord.objects.filter(timestamp__gte=start)
    return _export_report(records, 'daily-energy-report', request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_monthly(request):
    start = datetime.utcnow() - timedelta(days=30)
    records = EnergyRecord.objects.filter(timestamp__gte=start)
    return _export_report(records, 'monthly-energy-report', request)


def _export_report(records, filename_prefix, request):
    report_type = request.query_params.get('format', 'csv')
    if report_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Machine', 'Voltage', 'Current', 'Power kW', 'Energy kWh', 'Timestamp'])
        for record in records.select_related('machine'):
            writer.writerow([
                record.machine.name,
                record.voltage,
                record.current,
                record.power_kw,
                record.energy_kwh,
                record.timestamp.isoformat(),
            ])
        return response

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(filename_prefix)
    pdf.drawString(30, 750, filename_prefix.replace('-', ' ').title())
    y = 720
    for record in records.select_related('machine')[:40]:
        pdf.drawString(
            30,
            y,
            f"{record.timestamp:%Y-%m-%d %H:%M} | {record.machine.name} | {record.power_kw:.2f} kW",
        )
        y -= 18
        if y < 40:
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename_prefix}.pdf"'
    return response
