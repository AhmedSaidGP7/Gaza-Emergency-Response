from django.contrib import admin
from django.db import models
from .models import*




admin.site.register(Shelter)
admin.site.register(Governorate)
admin.site.register(Entity)
admin.site.register(Hospital)
admin.site.register(NGO)
admin.site.register(Building)
admin.site.register(Apartment)
admin.site.register(Dontation)
admin.site.register(Location)
admin.site.register(UploadedDocument)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_per_page = 1500

@admin.register(Person) 
class PersonAdmin(admin.ModelAdmin):
    list_per_page = 1500