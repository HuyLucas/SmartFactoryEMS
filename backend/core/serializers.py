from rest_framework import serializers
from .models import Machine, EnergyRecord, Alert


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'


class EnergyRecordSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source='machine.name', read_only=True)
    workshop_area = serializers.CharField(source='machine.workshop_area', read_only=True)

    class Meta:
        model = EnergyRecord
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source='machine.name', read_only=True)

    class Meta:
        model = Alert
        fields = '__all__'
