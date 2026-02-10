from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MachineViewSet,
    EnergyRecordViewSet,
    AlertViewSet,
    EnergyIngestView,
    dashboard_summary,
    report_daily,
    report_monthly,
)

router = DefaultRouter()
router.register(r'machines', MachineViewSet)
router.register(r'energy-records', EnergyRecordViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('energy/ingest/', EnergyIngestView.as_view(), name='energy-ingest'),
    path('dashboard/summary/', dashboard_summary, name='dashboard-summary'),
    path('reports/daily/', report_daily, name='report-daily'),
    path('reports/monthly/', report_monthly, name='report-monthly'),
]
