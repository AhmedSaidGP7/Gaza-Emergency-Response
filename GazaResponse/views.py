from django.http import HttpResponse, HttpResponseRedirect  
import datetime
from django.urls import reverse
from .models import *
# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from geopy.distance import geodesic
from django.core.files.storage import FileSystemStorage


@login_required
def check_arrival(request):
    if request.method == 'POST':
        user = request.user
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))

        # Geofence center and radius (example values)
        geofence_center = (29.939478049238794, 32.56028769414823)
        geofence_radius = 500  # in meters

        # Calculate distance
        distance = geodesic(geofence_center, (latitude, longitude)).meters
        if distance <= geofence_radius:
            # Log arrival
            VolunteerArrival.objects.create(volunteer=user)
            return JsonResponse({'status': 'success', 'message': 'Arrival recorded.'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'You are not within the geofenced area.'})

    return render(request, 'gaza/check_arrival.html')
