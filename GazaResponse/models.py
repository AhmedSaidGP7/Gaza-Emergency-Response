from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import pytesseract
import re
# Create your models here.

# This class represents the governorates with which we deal, whether they have service centers or hospitals.
class Governorate(models.Model):
    governorateName = models.CharField(max_length = 64)
    def __str__(self):
        return f'{self.governorateName}'

# This class represents the entities we interact with, such as the Ministry of Social Solidarity
# the Ministry of Health, the Ministry of Higher Education, etc.
class Entity(models.Model):
    name = models.CharField(max_length = 64)
    def __str__(self):
        return f'{self.name}'

# This class represents the hospitals where we receive patients from.
class Hospital(models.Model):
    name = models.CharField(max_length = 64)
    description = models.CharField(max_length = 64)
    hEntity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    hGovernorate = models.ForeignKey(Governorate, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.name}'

# This class represents the NGOs.
class NGO(models.Model):
    ngoName = models.CharField(max_length = 64)    
    def __str__(self):
        return f'{self.ngoName}'

# This class represents the shelters
class Shelter(models.Model):
    shelterName = models.CharField(max_length = 64)
    bGovernorate = models.ForeignKey(Governorate, on_delete = models.CASCADE, null = True)
    isWorking  = models.BooleanField(default = True)
    def __str__(self):
        return f'{self.shelterName}'

# Model representing a geographic location with latitude and longitude coordinates associated with each shelter.
class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)


# This class represents the buildings owned by the Ministry of Social Solidarity and
# designated for housing the affected individuals and their companions, such as
# the "Al-Khayalah" building and "Al-A'bor" building, etc.
class Building(models.Model):
    name = models.CharField(max_length = 64)
    address = models.TextField(max_length = 150 , blank = True)
    numOfFloors = models.IntegerField()
    accessibility = models.BooleanField()
    bshelter = models.ForeignKey(Shelter, on_delete = models.CASCADE, related_name = "Buildings")
    bGovernorate = models.ForeignKey(Governorate, on_delete = models.CASCADE)
    def __str__(self):
        return f'{"عمارة"} {self.name}'

# This class represents apartments in buildings or room. The apartment number represents the apartment
# number in the case of buildings or the room number in the case of relief centers. Capacity represents the
# number of beds in the location, and accessibility indicates whether the place is suitable for people with
# amputations in one of the feet/fractures.
class Apartment(models.Model):
    apartmentNum = models.IntegerField()
    whichBuilding = models.ForeignKey(Building, on_delete = models.CASCADE, related_name="apartments")
    apartmentCapacity = models.IntegerField()
    apartmentAccessibility = models.BooleanField()
    code = models.CharField(max_length = 64, blank=True)
    def __str__(self):
        return f'{"شقة"} {self.apartmentNum} - {self.whichBuilding} - {self.whichBuilding.bshelter}'

# This class represents the family or group to which the individual belongs.
# Since each person affected has companions connecting them, it is assumed that
# each person belongs to a group representing the family.
class Group(models.Model):
    groupName = models.CharField(max_length = 64)
    def __str__(self):
        return f'{self.groupName}'


# This class represents individuals. Both the affected and the companions must belong to a
# family, must be coming from a hospital, and must be residents in one of our shelter facilities.
# The "status" indicates whether they have been accommodated or have evacuated the place.
# "isDisabled" indicates whether they have fractures or amputations in the foot that prevent
# them from climbing stairs. "Has cancer" indicates whether they are affected by cancer or not.
# The property "type" indicates whether it is a patient (affected) or a companion.
class Person(models.Model):
    name = models.CharField(max_length = 64)
    profile_pic = models.ImageField(upload_to="ProfilePics", blank = True)
    birthday = models.DateField()
    theType = models.CharField(max_length = 64)
    gender = models.CharField(max_length = 64, default = 'ذكر')
    idNumber = models.CharField(max_length = 64)
    code = models.CharField(max_length = 64, blank=True)
    status = models.CharField(max_length = 64)
    phoneNumber = models.CharField(max_length = 64, blank=True)
    isDisabled  = models.BooleanField(default = False)
    hasCancer = models.BooleanField(default = False)
    personGroup = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="relatives")
    pHospital = models.ForeignKey(Hospital, on_delete = models.CASCADE)
    diagnosis = models.TextField(blank = True)
    accommodation  = models.ForeignKey(Apartment, on_delete = models.CASCADE, related_name="residents")
    scannedDocs = models.FileField(upload_to="IDs", blank=True)
    entryDate =  models.DateField(null=True, blank=True)
    hostingStartDate = models.DateField(null=True, blank=True)
    def __str__(self):
        return f'{self.name}'






class Dontation(models.Model):
    date = models.DateTimeField()
    org = models.ForeignKey(NGO, on_delete = models.CASCADE, related_name="Donors")
    toBuilding = models.ForeignKey(Building, on_delete = models.CASCADE, related_name="ReceivedGifts")
    itemsName = models.CharField(max_length = 32)
    quantity = models.IntegerField()
    personWhoReceived = models.CharField(max_length = 64)
    def __str__(self):
        return f'{self.itemsName} - {self.toBuilding}'






class logOutLogs(models.Model):
    date = models.DateField()
    person = models.ForeignKey(Person, on_delete = models.CASCADE, related_name="departures")
    scannedDocs = models.FileField(upload_to="LogOutLogs", blank=True)
    def __str__(self):
        return f'{self.person}'





class UploadedDocument(models.Model):
    document = models.FileField(upload_to="uploaded_documents")
    title = models.CharField(max_length=255, blank=True)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name="documents", null=True)
    id_number = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.document.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Document for {self.person.name if self.person else 'Unknown'}"
