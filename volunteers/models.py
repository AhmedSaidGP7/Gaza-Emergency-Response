from django.db import models
from GazaResponse.models import *

# Create your models here.
class Visit(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    Shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    log_in_time = models.DateTimeField(auto_now_add=True)
    log_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.volunteer.username} visit to {self.Shelter.shelterName}'