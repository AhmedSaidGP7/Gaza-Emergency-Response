from django.db import models
from GazaResponse.models import *

# Create your models here.


class ambulance_log(models.Model):
    casualty = models.ForeignKey(Person, on_delete = models.CASCADE, related_name="ambulance_requests")
    report_num =  models.IntegerField()
    ambulance_code = models.CharField(max_length = 32)
    paramedic_name =  models.CharField(max_length = 64)
    paramedic_phone =  models.CharField(max_length = 64)
    hospital = models.ForeignKey(Hospital, on_delete = models.CASCADE, null=True)
    fees =  models.CharField(max_length = 64, null=True, blank=True)
    scannedDocs = models.FileField(upload_to="medical-reports", blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    def __str__(self):
        return f'المصاب {self.casualty} بلاغ رقم {self.report_num}'
    class Meta:
        ordering = ['-date']  # Order by publish_date descending

class diseases(models.Model):
    diseases_name = models.CharField(max_length = 64)
    def __str__(self):
        return f"{self.diseases_name}"  


class AffectedBy(models.Model):
    person = models.ForeignKey(Person, on_delete = models.CASCADE, related_name="affected_by")
    diseases_name = models.ForeignKey(diseases, on_delete = models.CASCADE, related_name="affected_persons")
    def __str__(self):
        return f"{self.person} is affected by {self.diseases_name}"  