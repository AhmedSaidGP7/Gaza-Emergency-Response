from django.shortcuts import render, get_object_or_404
from GazaResponse.models import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        name = request.POST.get("casualty")
        report_num = request.POST.get("report_num")
        if not name or not report_num or not report_num.isdigit():
            return render(request, "medical/ambulance.html", {
            "errorMessage" : "برجاء ادخال جميع الحقول وبشكل صحيح",
            "Persons" : Person.objects.all(),
            "Hospitals": Hospital.objects.all(),
            "report_num": report_num,
        })

        # Check if the person exists in the DB
        report_num_exists = ambulance_log.objects.filter(report_num = report_num)
        if report_num_exists:
            return render(request, "medical/ambulance.html", {
                "errorMessage" : f"البلاغ رقم {report_num} موجود سابقًا",
                "Persons" : Person.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "report_num": report_num,
            })
        # Get the instance of 
        try:
            person = Person.objects.get(id=name)
        except ObjectDoesNotExist:
            return render(request, 'medical/upload_excel.html', {
                "errorMessage": f"المستشفى '{hospital_name}' غير مسجلة لدينا. برجاء التواصل مع الدعم الفني."
        })

        personNameInst = Person.objects.get(id = name)
        # Inserting the date into the database
        add_new_ambulance_record = ambulance_log.objects.create(
            casualty = personNameInst,
            report_num = report_num
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
    else:
        person_ids = request.POST.getlist("names[]")
        disease_ids = request.POST.getlist("diseases[]")
        
        if not person_ids or not disease_ids:
            return render(request, 'medical/assign_diseases.html', {
            'errorMessage': "برجاء إدخال جميع الحقول المطلوبة.",   
            'Persons': Person.objects.all(),
            'diseases': diseases.objects.all()
        })

        # Validate the person data
        for person_id in person_ids:
            if not person_id.isdigit():
                return render(request, 'medical/assign_diseases.html', {
                    'errorMessage': "معرف الشخص المدخل خاطئ",
                    'Persons': Person.objects.all(),
                    'diseases': diseases.objects.all()
                })
            try:
                person_instance = Person.objects.get(id=person_id)
            except ObjectDoesNotExist:
                 return render(request, 'medical/assign_diseases.html', {
                    'errorMessage': "احد الاشخاص المدخلين غير موجود في قواعد البيانات",    
                    'Persons': Person.objects.all(),
                    'diseases': diseases.objects.all()
                })
        if not person_ids or not disease_ids:
            return render(request, 'medical/assign_diseases.html', {
            'errorMessage': "برجاء إدخال جميع الحقول المطلوبة.",   
            'Persons': Person.objects.all(),
            'diseases': diseases.objects.all()
        })

        # Validate the disease data
        for disease_id in disease_ids:
            if not disease_id.isdigit():
                return render(request, 'medical/assign_diseases.html', {
                    'errorMessage': "معرف المرض المدخل خاطئ",
                    'Persons': Person.objects.all(),
                    'diseases': diseases.objects.all()
                })
            try:
                disease_instance = diseases.objects.get(id=disease_id)
            except ObjectDoesNotExist:
                 return render(request, 'medical/assign_diseases.html', {
                    'errorMessage': "احد التشخيصات المدخلة غير موجودة في قواعد البيانات",    
                    'Persons': Person.objects.all(),
                    'diseases': diseases.objects.all()
                })

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
            'message': "تم إتخاذ الإجراء المطلوب",
            'Persons': Person.objects.all(),
            'diseases': diseases.objects.all()
        })


@login_required
def ambulance_log_detail(request, id):
    if request.method == 'GET':
        log = get_object_or_404(ambulance_log, id=id)
        return render(request, 'medical/ambulance_log_detail.html', {
            "log": log,
            "Hospitals": Hospital.objects.all(),
            "People": Person.objects.all(),
        })

    else:
        # Handle the POST data
        ambulance_code = request.POST.get("ambulance_code")
        paramedic_name = request.POST.get("paramedic_name")
        paramedic_phone = request.POST.get("paramedic_phone")
        fees = request.POST.get("fees")
        hospital_id = request.POST.get("Hospital")
        scannedDocs = request.FILES.get("uploadedfile")
        arrival_time = request.POST.get("arrival_time")
        status = request.POST.get("status")
        companion = request.POST.get("companion")

        if arrival_time:
            arrival_time = datetime.strptime(arrival_time, '%H:%M').time()
     


        # Check if required fields are filled
        if not ambulance_code or not paramedic_name or not paramedic_phone or not arrival_time or not status:
            return render(request, 'medical/ambulance_log_detail.html', {
                "errorMessage": "حدث خطأ اثناء الإدخال, برجاء التواصل مع الدعم الفني.",
                "log": ambulance_log.objects.get(id=id),
                "Hospitals": Hospital.objects.all(),
                "People": Person.objects.all(),
            })

        # Validate hospital_id
        if not hospital_id.isdigit() or not companion.isdigit():
            return render(request, 'medical/ambulance_log_detail.html', {
                "errorMessage": "حدث خطأ اثناء الإدخال, برجاء التواصل مع الدعم الفني.",
                "log": ambulance_log.objects.get(id=id),
                "Hospitals": Hospital.objects.all(),
                "People": Person.objects.all(),
            })

        
        try:
            if hospital_id and hospital_id != '0':
                hospital_instance = Hospital.objects.get(id=hospital_id)
            else:
                hospital_instance = None

            if companion and companion != '0':
                companion_instance = Person.objects.get(id=companion)
            else:
                companion_instance = None

        except ObjectDoesNotExist:
            return render(request, 'medical/ambulance_log_detail.html', {
                "errorMessage": "حدث خطأ في الإدخال, برجاء اعادة المحاولة",
                "log": ambulance_log.objects.get(id=id),
                "Hospitals": Hospital.objects.all(),
                "People": Person.objects.all(),
            })

        # Update the ambulance log record
        log = ambulance_log.objects.get(id=id)
        log.ambulance_code = ambulance_code
        log.paramedic_name = paramedic_name
        log.paramedic_phone = paramedic_phone
        log.fees = fees
        log.status = status
        if companion_instance:
            log.companion = companion_instance
        log.arrival_time = arrival_time
        if hospital_instance:
            log.hospital = hospital_instance
        if scannedDocs:
            log.scannedDocs = scannedDocs
        log.save()

        return render(request, 'medical/ambulance_log_detail.html', {
            "message": "تم تعديل البلاغ بنجاح!",
            "log": log,
            "Hospitals": Hospital.objects.all(),
            "People": Person.objects.all(),
        })


@login_required
def ambulance_record_detail(request, id):

    log = get_object_or_404(ambulance_log, id=id)
    return render(request, 'medical/ambulance_record_detail.html', {
        "log": log,
        "Hospitals": Hospital.objects.all(),
        "People": Person.objects.all(),

    })



@login_required
def uploadMedicalFile(request):
    if request.method == 'GET':
        return render(request, 'medical/upload_medical_file.html', {'Persons': Person.objects.all()})

    elif request.method == 'POST':
        # Handle the POST data
        person_id = request.POST.get("name")
        uploaded_files = request.FILES.getlist("document")

        # Check if uploaded_files is empty
        if not uploaded_files:
            return render(request, 'medical/upload_medical_file.html', {
                "errorMessage": "يجب رفع مستند واحد على الأقل.",
                "Persons": Person.objects.all(),
            })

        # Check if person_ids is empty or contains non-digit values
        if not person_id:
            return render(request, 'medical/upload_medical_file.html', {
                "errorMessage": "يجب تحديد اسم المستفيد.",
                "Persons": Person.objects.all(),
            })


        if not person_id.isdigit():
            return render(request, 'medical/upload_medical_file.html', {
                "errorMessage": "حدث خطأ في الرفع، معرف الشخص غير صحيح.",
                "Persons": Person.objects.all(),
            })

        # Upload the docs for selected person
        try:
            person = Person.objects.get(id=person_id)
        except ObjectDoesNotExist:
            return render(request, 'medical/upload_medical_file.html', {
                "errorMessage": "حدث خطأ في الإدخال, برجاء اعادة المحاولة",
                "Persons": Person.objects.all(),
            })

        for uploaded_file in uploaded_files:
            UploadMedicalDoc.objects.create(
                person=person,
                document=uploaded_file,
                title=uploaded_file.name  # Ensure title is set to file name
            )

        return render(request, "medical/upload_medical_file.html", {
            "message": "تم رفع المستندات بنجاح",
            "Persons": Person.objects.all(),
        })

    # Handle case where method is not GET or POST
    return render(request, 'medical/upload_medical_file.html', {'Persons': Person.objects.all()})

    


@login_required
def create_diagnose(request):
    if request.method == 'GET':
        return render(request, 'medical/create_dignose.html', {'Persons': Person.objects.all()})
    else:
        # Handle the POST data
        patient = request.POST.get("patient")
        diagnose_type = request.POST.get("diagnose_type")
        diagnose = request.POST.get("diagnosis")

        # Validate data
        if not diagnose or not diagnose_type or not patient or not patient.isdigit():
            return render(request, 'medical/create_dignose.html', {
                'errorMessage': "حدث خطأ في الإدخال, يرجى المحاولة مرة اخرى.",
                'Persons': Person.objects.all()
                })

        try:
            patient = Person.objects.get(id = patient)
        except ObjectDoesNotExist:
            return render(request, 'medical/create_dignose.html', {
                'errorMessage': "الشخص المدخل غير موجود في قواعد البيانات.",
                'Persons': Person.objects.all()
                })
    
        # Insert into DB
        Diagnose.objects.create(
                patient=patient,
                diagnose_type=diagnose_type,
                diagnose=diagnose 
            )

        # Return HTTP Object
        return render(request, 'medical/create_dignose.html', {
            'message': "تم إضافة التشخيص لملف المريض",
            'Persons': Person.objects.all()
            })



# Medical Case management
@login_required
def addPost(request):
    if request.method == "GET":
        return render(request, 'medical/add_post.html', {
            "Persons": Person.objects.all(),

        })
    else:
        # Handle the POST request
        title = request.POST.get("title")
        patient = request.POST.get("thename")
        content = request.POST.get("content")
        ticketScannedDocs = request.FILES.get("uploadedfile", False)
        is_urgent = request.POST.get("theType")
        actual_date = request.POST.get('date')
        
        # Validate the data
        if not title or not patient or not content or not is_urgent or not actual_date or not patient.isdigit():
            return render(request, 'medical/add_post.html',
            {
                'errorMessage': "برجاء إدخال جميع البيانات وبشكل صحيح",
                'Persons' : Person.objects.all(),
            })

        try:
            patient = Person.objects.get(id = patient)
        except ObjectDoesNotExist:
            return render(request, 'medical/add_post.html',
            {
                'errorMessage': "الأسم الذي تم ادخاله غير موجود في قواعد البيانات.",
                'Persons' : Person.objects.all(),
            })

        try:
            actual_date = datetime.strptime(actual_date, '%Y-%m-%d')
          
        except ValueError as e:
             return render(request, 'medical/add_post.html',
            {
                'errorMessage': "صيغة التاريخ مدخلة بشكل خاطئ",
                'Persons' : Person.objects.all(),
            })



        if is_urgent == 'True':
            is_urgent = True
        else:
            is_urgent = False

        user = request.user
        Medical_Intervention.objects.create(
            title = title,
            patient = patient,
            is_urgent = is_urgent,
            content = content,
            ticketScannedDocs = ticketScannedDocs,
            author= user,  
            caseResponsible= user,
            actual_date = actual_date,
        )
        return render(request, "medical/add_post.html", {
                "message" : "تم إضافة المستفيد بنجاح!",
                "Persons": Person.objects.all(),

            }) 

@login_required
def retrieveAllPosts(request):
    return render(request, "medical/all_posts.html", {
        "persons": Person.objects.all(),
        "tickets": Medical_Intervention.objects.all(),
        "users": User.objects.all()
    })



@login_required
def retrieveSomePosts(request):
    whichCases = request.POST.get("whichCases")
    if whichCases == '1':
        cases = Medical_Intervention.objects.filter(status="جديد")
    elif whichCases == '2':
        cases = Medical_Intervention.objects.filter(status="جارية")
    elif whichCases == '3':
        cases = Medical_Intervention.objects.filter(status="مغلقة")
    elif whichCases == '4':
        cases = Medical_Intervention.objects.filter(is_urgent= True)
    elif whichCases == '5':
        cases = Medical_Intervention.objects.filter(is_urgent= False)
    elif whichCases == '0':
        cases = Medical_Intervention.objects.all()
    else:
        cases = Medical_Intervention.objects.none()  # Default to an empty queryset if no valid option is selected

    return render(request, "medical/all_posts.html", {
        "persons": Person.objects.all(),
        "tickets": cases,
        "users": User.objects.all()
    })

@login_required
def serachPost(request):
    query = request.GET.get('query', '')
    results = Medical_Intervention.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(patient__idNumber__icontains=query) |
                Q(patient__name__icontains=query) |
                Q(patient__phoneNumber__icontains = query)
            )   
    return render(request, "medical/all_posts.html", {
        "persons": Person.objects.all(),
        "tickets": results,
        "users": User.objects.all()
    })




@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Medical_Intervention, id=ticket_id)
    return render(request, 'medical/ticket_detail.html', {
        'ticket': ticket,
        "persons": Person.objects.all(),
        "users": User.objects.all(),
        "comments": Medical_Intervention_comments.objects.filter(ticket = ticket)
    })


@login_required
def CloseCase(request):
    caseID =  request.POST.get("caseID")
    case = get_object_or_404(Medical_Intervention, id=caseID)
    case.status = 'مغلقة'
    case.save()
    return HttpResponseRedirect(reverse('medical:allposts'))

@login_required
def addComment(request):
    caseID = request.POST.get("theticket")
    comment = request.POST.get("comment")
    CommentScannedDocs = request.FILES.get("uploadedfile", False)
    user = request.user
    case = get_object_or_404(Medical_Intervention, id=caseID)
    newComment = Medical_Intervention_comments.objects.create(
        author= user,
        content = comment,
        ticket = case,
        CommentScannedDocs = CommentScannedDocs

    )
    case.status = 'جارية'
    case.save()
    return HttpResponseRedirect(reverse('medical:ticket_detail', args=[case.id]))
