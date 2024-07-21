from django.shortcuts import render
from GazaResponse.models import *
from django.contrib.auth.decorators import login_required
from .models import *

# Create your views here.

@login_required
def ambulance(request):
    if request.method == "GET":    
        return render(request, 'medical/ambulance.html', {
            "Persons" : Person.objects.all(),
            "Hospitals": Hospital.objects.all(),
        })
    else:
        # Handle the POST date
        name = request.POST["casualty"]
        report_num = request.POST["report_num"]
        ambulance_code = request.POST["ambulance_code"]
        paramedic_name = request.POST["paramedic_name"]
        paramedic_phone = request.POST["paramedic_phone"]
        theHospital = request.POST["Hospital"]
        fees = request.POST["fees"]
        uploadedfile = request.FILES.get("uploadedfile", False)
       

        # Check if the person exists in the DB
        report_num_exists = ambulance_log.objects.filter(report_num = report_num)
        if report_num_exists:
            return render(request, "medical/ambulance.html", {
                "errorMessage" : "Error",
                "Persons" : Person.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "report_num": report_num,
            })
        # Get the instance of 
        hosptialInst = Hospital.objects.get(id = theHospital)
        personNameInst = Person.objects.get(id = name)

        # Inserting the date into the database
        add_new_ambulance_record = ambulance_log.objects.create(
            casualty = personNameInst,
            report_num = report_num,
            ambulance_code = ambulance_code,
            paramedic_name = paramedic_name,
            paramedic_phone = paramedic_phone,
            hospital = hosptialInst,
            scannedDocs = uploadedfile,
            fees = fees,
        )
        return render(request, "medical/ambulance.html", {
                "message" : "تم تسجيل البلاغ بنجاح",
                "Persons" : Person.objects.all(),
                "Hospitals": Hospital.objects.all(),

            })     


@login_required
def ambulancelog(request):
    return render(request, 'medical/ambulance_log.html', {
        "ambulance_logs": ambulance_log.objects.all(),  # Changed key name to plural
    })



@login_required
def assign_diseases(request):
    if request.method == 'GET':
        return render(request, 'medical/assign_diseases.html', {
            'Persons': Person.objects.all(),
            'diseases': diseases.objects.all()
        })
    elif request.method == 'POST':
        person_ids = request.POST.getlist("names[]")
        disease_ids = request.POST.getlist("diseases[]")

        # Create AffectedBy objects for each person-disease pair
        for person_id in person_ids:
            person = Person.objects.get(id=person_id)
            for disease_id in disease_ids:
                disease = diseases.objects.get(id=disease_id)
                
                # Check if the AffectedBy object already exists
                if not AffectedBy.objects.filter(person=person, diseases_name=disease).exists():
                    AffectedBy.objects.create(
                        person=person,
                        diseases_name=disease
                    )

        return render(request, 'medical/assign_diseases.html', {
            'message': "تم إضافة الأمراض بنجاح",
            'Persons': Person.objects.all(),
            'diseases': diseases.objects.all()
        })
