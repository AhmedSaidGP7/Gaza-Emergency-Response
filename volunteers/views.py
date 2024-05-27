from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
import datetime
from GazaResponse.models import *
from django.contrib.auth.models import User
# views.py
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from django.contrib.auth.decorators import login_required
from geopy.distance import geodesic

def check_arrival(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    if request.method == 'POST':
        user = request.user
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))

         # Check if the user has an open visit
        if Visit.objects.filter(volunteer=user, log_out_time__isnull=True).exists():
            return JsonResponse({'message': 'لديك زيارة مفتوحة بالفعل. يجب عليك تسجيل إنصراف لتلك الزيارة قبل تسجيل زيارة جديدة'}, status=400)

        locations = Location.objects.all()
        for location in locations:
            shelter_coords = (location.latitude, location.longitude)
            user_coords = (latitude, longitude)
            distance = geodesic(shelter_coords, user_coords).meters
            if distance <= 500:
                Visit.objects.create(volunteer=user, Shelter=location.shelter)
                return JsonResponse({'status': 'success', 'message': 'تم تسجيل زيارتك لـ ' + location.shelter.shelterName})
        
        return JsonResponse({'status': 'fail', 'message': 'انت لست ضمن احد مشاريع خدمة الإيواء'})
    
    return render(request, 'volunteers/check_arrival.html')


def check_departure(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    if request.method == 'POST':
        user = request.user
        try:
            visit = Visit.objects.filter(volunteer=user, log_out_time__isnull=True).latest('log_in_time')
            visit.log_out_time = timezone.now()
            visit.save()
            return JsonResponse({'status': 'success', 'message': 'تم تسجيل إنصرافك! شكرا لتطوعك معنا!'})
        except Visit.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'يبدوا انك نسيت تسجيل حضورك.'})

    return render(request, 'volunteers/check_departure.html')