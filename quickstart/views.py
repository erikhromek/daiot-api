from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from daiot_api.quickstart.models import Device, Measurement
from daiot_api.quickstart.serializers import (
    DeviceSerializer,
    MeasurementSerializer,
    UserSerializer,
    GroupSerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone

from daiot_api.quickstart.mqtt import client as mqtt_client
from django.http import JsonResponse


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by("-id")
    serializer_class = DeviceSerializer


class DeviceApiView(APIView):
    # 1. List all
    def get(self, request, *args, **kwargs):
        """
        List all the devices
        """
        devices = Device.objects.filter()
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        """
        Create the Device with given Device data
        """
        data = {
            "id": request.data.get("id"),
            "name": request.data.get("name"),
            "location": request.data.get("location"),
            "enabled": True,
        }
        serializer = DeviceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceDetailApiView(APIView):
    def get(self, request, device_id, *args, **kwargs):
        try:
            device = Device.objects.get(id=device_id)
            serializer = DeviceSerializer(device)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"message": "Device does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class MeasurementApiView(APIView):
    # 1. List all
    def get(self, request, device_id, *args, **kwargs):
        """
        List all the measurements for a device
        """
        try:
            Device.objects.get(id=device_id)
            this_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
            one_hour_before = this_hour - timedelta(hours=1)
            measurements = (
                Measurement.objects.filter(
                    device_id=device_id, datetime__range=(one_hour_before, this_hour)
                )
                .order_by("datetime")
                .values()
            )

            serializer = MeasurementSerializer(measurements, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"message": "Device does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )

    # 2. Create
    def post(self, request, device_id, *args, **kwargs):
        """
        Create the Measurement with given Measurement data
        """

        try:
            device = Device.objects.get(id=device_id)
            data = {
                "datetime": request.data.get("datetime"),
                "temperature": request.data.get("temperature"),
                "pressure": request.data.get("pressure"),
                "humidity": request.data.get("humidity"),
                "device_id": device.id,
            }

            serializer = MeasurementSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(
                {"message": "Device does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )


def publish_message(request, device_id):
    try:
        device = Device.objects.get(id=device_id)
        rc, mid = mqtt_client.publish(f"/commands/{device.id}", "Example command")
        return JsonResponse({"code": rc})
    except ObjectDoesNotExist:
        return Response(
            {"message": "Device does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )


class PublishApiView(APIView):
    # 2. Create
    def post(self, request, device_id, *args, **kwargs):
        try:
            device = Device.objects.get(id=device_id)
            rc, mid = mqtt_client.publish(f"/commands/{device.id}", "Example command")
            return JsonResponse({"code": rc})
        except ObjectDoesNotExist:
            return Response(
                {"message": "Device does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )