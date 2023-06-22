from django.contrib.auth.models import User, Group
from rest_framework import serializers

from daiot_api.quickstart.models import Device, Measurement


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class MeasurementSerializer(serializers.ModelSerializer):
    device_id = serializers.PrimaryKeyRelatedField(queryset = Device.objects.all(), source = 'device', allow_null = False, write_only=True)

    class Meta:
        model = Measurement
        fields = ['id', 'datetime', 'device_id', 'temperature', 'pressure', 'humidity']

class DeviceSerializer(serializers.ModelSerializer):
    last_measurement = MeasurementSerializer(allow_null = True, read_only=True)
    class Meta:
        model = Device
        fields = ['id', 'name', 'location', 'last_measurement']

    
