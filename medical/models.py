from django.db import models
from GazaResponse.models import *

# Create your models here.


class ambulance_log(models.Model):
    casualty = models.ForeignKey(Person, on_delete = models.CASCADE, related_name="ambulance_requests")
    report_num =  models.IntegerField()
    ambulance_code = models.CharField(max_length = 32, blank=True)
    paramedic_name =  models.CharField(max_length = 64, blank=True)
    paramedic_phone =  models.CharField(max_length = 32, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete = models.CASCADE, null=True, blank=True)
    fees =  models.CharField(max_length = 64, null=True, blank=True)
    scannedDocs = models.FileField(upload_to="medical-reports", blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.CharField(max_length = 64, null=True, blank=True, default = "لم يحضر الإسعاف")
    arrival_time = models.TimeField(null=True, blank=True)
    companion = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='companions')
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


class UploadMedicalDoc(models.Model):
    document = models.FileField(upload_to="medical_documents")
    title = models.CharField(max_length=255, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="medicalDocuments", null=True)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.document.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Document for {self.person.name if self.person else 'Unknown'}"


class Diagnose(models.Model):
    patient = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="diagnoses", null=True)
    diagnose_type = models.CharField(max_length=64, blank=True)
    diagnose = models.TextField(blank = True)
    def __str__(self):
        return f"{self.patient}"  


class Medical_Intervention(models.Model):
    title = models.CharField(max_length = 32)
    patient = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="Medical_Interventions")
    status = models.CharField(max_length = 32, default="جديد")
    is_urgent = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True)
    actual_date = models.DateField( blank=True)
    content = models.TextField()
    ticketScannedDocs = models.FileField(upload_to="medical_interventions_docs", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_Interventions")
    caseResponsible = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Interventions_responsible")
    def __str__(self):
        return f'{self.title}'

class Medical_Intervention_comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Medica_authorComments")
    date = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.TextField()
    CommentScannedDocs = models.FileField(upload_to="medical_interventions_docs", blank=True)
    ticket = models.ForeignKey(Medical_Intervention, on_delete=models.CASCADE, related_name="Medical_Intervention_comments")