from django.contrib import admin
from .models import*

# Register your models here.
admin.site.register(ambulance_log)
admin.site.register(diseases)
admin.site.register(AffectedBy)
admin.site.register(UploadMedicalDoc)
admin.site.register(Diagnose)
admin.site.register(Medical_Intervention)
admin.site.register(Medical_Intervention_comments)
