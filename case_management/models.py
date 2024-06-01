from django.db import models
from GazaResponse.models import *
# Create your models here.


class Tickets(models.Model):
    title = models.CharField(max_length = 32)
    belongsTo = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="PersonTickets")
    status = models.CharField(max_length = 32)
    is_urgent = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.TextField()
    ticketScannedDocs = models.FileField(upload_to="Tickets", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authorTickets")
    caseResponsible = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responsible")
    def __str__(self):
        return f'{self.title}'


class comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authorComments")
    date = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.TextField()
    CommentScannedDocs = models.FileField(upload_to="Comments", blank=True)
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name="comments")
