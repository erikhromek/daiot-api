from datetime import datetime
from json import JSONDecodeError
import json
import paho.mqtt.client as mqtt
from django.conf import settings
import ssl
from django.core.exceptions import ObjectDoesNotExist

from daiot_api.quickstart.models import Device
from daiot_api.quickstart.serializers import MeasurementSerializer


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe('/measurements')
    else:
        print('Bad connection. Code:', rc)


def on_message(mqtt_client, userdata, msg):
    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
    try:

        message = json.loads(msg.payload)
        data = {
            'datetime': datetime.now(), 
            'temperature': message['temperature'], 
            'pressure': message['pressure'],
            'humidity': message['humidity'],
            'device_id': message['deviceId']
            }
        device = Device.objects.get(id=data['device_id'])

        serializer = MeasurementSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print(f'Saved data from device {device.id}')
        else:
            print(f'Received invalid data from device {device.id}')
                

    except KeyError:
        print('Error reading broker data from /measurements')
    except ObjectDoesNotExist:
        print('Received data from an unknown device')
    except JSONDecodeError:
        print('Error reading data from device')

client = mqtt.Client()
client.tls_set(ca_certs='certs/ca.crt',certfile='certs/client.crt',keyfile='certs/client.key', tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_SERVER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)