from django.db import models

class Device(models.Model):
    id = models.CharField(primary_key=True, max_length=18)
    name = models.CharField(max_length=32)
    location = models.CharField(max_length=64, blank=True)
    enabled = models.BooleanField(default=True)

    @property
    def last_measurement(self):
        return Measurement.objects.filter(device=self).last()

class Measurement(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='measurements', blank=False, null=False)
    datetime = models.DateTimeField(blank=False, null=False)
    pressure = models.FloatField(null=False)
    humidity = models.FloatField(null=False)
    temperature = models.FloatField(null=False)

    @property
    def device_id(self):
        return self.device.id