from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import datetime
from GazaResponse.models import *
from medical.models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist  
from dateutil import parser
from django.core.files.storage import FileSystemStorage
#import pytesseract
#from PIL import Image
#import re
from .forms import *
#from django.db import transaction
import os


@login_required
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file, dtype=str)

        # Check expected columns
        expected_columns = {'الاسم', 'المستشفى', 'النوع', 'رقم الهوية', 'التشخيص', 'تاريخ الميلاد', 
                            'رقم المبنى', 'رقم الوحدة/الغرفة', 'مقدم خدمة الإيواء', 'تاريخ تقديم خدمة الايواء', 
                            'تاريخ دخول مصر', 'رقم الهاتف المصري', 'الوضع الحالي'}
        if not expected_columns.issubset(df.columns):
            return render(request, 'operations/upload_excel.html', {
                "errorMessage": "ملف الـ Excel يحتوي على أعمدة غير متوقعة أو يفتقد إلى بعض الأعمدة المتوقعة."
            })

        # Check for valid dates and convert to None if invalid or empty
        def check_date(date_str):
            try:
                if pd.isna(date_str) or date_str == '':
                    return None
                return parser.parse(date_str).date()
            except (ValueError, TypeError):
                return None

        df['تاريخ الميلاد'] = df['تاريخ الميلاد'].apply(check_date)
        df['تاريخ دخول مصر'] = df['تاريخ دخول مصر'].apply(check_date)
        df['تاريخ تقديم خدمة الايواء'] = df['تاريخ تقديم خدمة الايواء'].apply(check_date)

        # Convert phone number column to string, ensuring zeros are preserved
        df['رقم الهاتف المصري'] = df['رقم الهاتف المصري'].apply(lambda x: str(x).strip() if pd.notna(x) else '')

        for index, row in df.iterrows():
            name = row['الاسم']
            # Check for mandatory field
            if not name:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"خانة الاسم الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })

            hospital_name = row['المستشفى']
            gender = row['النوع']
            # Check for mandatory field
            if not gender:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"خانة النوع الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            id_number = row['رقم الهوية']
            # Check for mandatory field
            if not id_number:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"خانة رقم الهوية الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            diagnosis = row['التشخيص']
            birthday = row['تاريخ الميلاد']
            building_number = row['رقم المبنى']
            apartment_number = row['رقم الوحدة/الغرفة']
            TheshelterName = row['مقدم خدمة الإيواء']
            hostingStartDate = row['تاريخ تقديم خدمة الايواء']
            entryDate = row['تاريخ دخول مصر']
            phoneNumber = row['رقم الهاتف المصري']
            status = row['الوضع الحالي']
            # Check for mandatory field
            if not status:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"خانة الوضع الحالي الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })

            try:
                hospital = Hospital.objects.get(name=hospital_name)
            except ObjectDoesNotExist:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"المستشفى '{hospital_name}' غير مسجلة لدينا. برجاء التواصل مع الدعم الفني."
                })

            try:
                shelter = Shelter.objects.get(shelterName=TheshelterName)
            except ObjectDoesNotExist:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"مقدم خدمة الإيواء '{TheshelterName}' غير مسجل لدينا. تأكد من كتابته بشكل صحيح مطابق لقواعد البيانات"
                })

            try:
                building = Building.objects.get(name=str(building_number), bshelter=shelter)
            except ObjectDoesNotExist:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"لا يوجد مبنى برقم '{building_number}' في موقع '{TheshelterName}'."
                })

            try:
                apartment = Apartment.objects.get(apartmentNum=apartment_number, whichBuilding=building)
            except ObjectDoesNotExist:
                return render(request, 'operations/upload_excel.html', {
                    "errorMessage": f"شقة رقم '{apartment_number}' غير موجودة في عمارة رقم '{building_number}'."
                })

            # Check if person with the same ID number already exists
            if Person.objects.filter(idNumber=id_number).exists():
                continue  # Skip this row if ID number already exists

            group, created = Group.objects.get_or_create(groupName=name)

            person = Person(
                name=name,
                birthday=birthday,
                theType='مصاب',
                idNumber=id_number,
                gender=gender,
                diagnosis=diagnosis,
                personGroup=group,
                pHospital=hospital,
                accommodation=apartment,
                status=status,
                phoneNumber=phoneNumber,
                entryDate=entryDate,
                hostingStartDate=hostingStartDate
            )
            person.save()

        return render(request, 'operations/upload_excel.html', {
            "message": "تم إضافة المصابيين بنجاح!"
        })

    return render(request, 'operations/upload_excel.html')


@login_required
def upload_excel_for_person(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file, dtype=str)

        # Check expected columns
        expected_columns = {'الاسم', 'المستشفى', 'النوع', 'رقم الهوية', 'التشخيص', 'تاريخ الميلاد', 
                            'رقم المبنى', 'رقم الوحدة/الغرفة', 'مقدم خدمة الإيواء', 'تاريخ تقديم خدمة الايواء', 
                            'تاريخ دخول مصر', 'رقم الهاتف المصري', 'الوضع الحالي', 'اسم المصاب'}
        if not expected_columns.issubset(df.columns):
            return render(request, 'operations/upload_excel.html', {
                "errorMessage": "ملف الـ Excel يحتوي على أعمدة غير متوقعة أو يفتقد إلى بعض الأعمدة المتوقعة."
            })


         # Check for valid dates and convert to None if invalid or empty
        def check_date(date_str):
            try:
                if pd.isna(date_str) or date_str == '':
                    return None
                return parser.parse(date_str).date()
            except (ValueError, TypeError):
                return None

        df['تاريخ الميلاد'] = df['تاريخ الميلاد'].apply(check_date)
        df['تاريخ دخول مصر'] = df['تاريخ دخول مصر'].apply(check_date)
        df['تاريخ تقديم خدمة الايواء'] = df['تاريخ تقديم خدمة الايواء'].apply(check_date)

        # Convert phone number column to string, ensuring zeros are preserved
        df['رقم الهاتف المصري'] = df['رقم الهاتف المصري'].apply(lambda x: str(x).strip() if pd.notna(x) else '')

        for index, row in df.iterrows():
            name = row['الاسم']
            # Check for mandatory field
            if not name:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة الاسم الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })

            hospital_name = row['المستشفى']
            if not hospital_name:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة المستشفى الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            gender = row['النوع']
            # Check for mandatory field
            if not gender:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة النوع الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            id_number = row['رقم الهوية']
            # Check for mandatory field
            if not id_number:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة رقم الهوية الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            casualty = row['اسم المصاب']  
            diagnosis = row['التشخيص']
            birthday = row['تاريخ الميلاد']
            building_number = row['رقم المبنى']
            if not building_number:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة رقم المبنى الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            apartment_number = row['رقم الوحدة/الغرفة']
            if not apartment_number:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة رقم الوحدة/الغرفة الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            TheshelterName = row['مقدم خدمة الإيواء']
            if not TheshelterName:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة رقم مقدم خدمة الإيواء الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })
            hostingStartDate = row['تاريخ تقديم خدمة الايواء']
            entryDate = row['تاريخ دخول مصر']
            phoneNumber = row['رقم الهاتف المصري']
            status = row['الوضع الحالي']
            # Check for mandatory field
            if not status:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"خانة رقم الوضع الحالي الزامية, لكنها غير موجودة في الصف رقم: {index + 1}."
                })

            try:
                hospital = Hospital.objects.get(name=hospital_name)
            except ObjectDoesNotExist:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"مستشفى '{hospital_name}' غير مسجلة لدينا."
                })

            try:
                shelter = Shelter.objects.get(shelterName=TheshelterName)
            except ObjectDoesNotExist:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f"مركز '{TheshelterName}' غير موجود."
                })

            try:
                building = Building.objects.get(name=str(building_number), bshelter=shelter)
            except ObjectDoesNotExist:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f" عمارة رقم '{building_number}' غير موجودة في '{TheshelterName}'."
                })

            try:
                apartment = Apartment.objects.get(apartmentNum=apartment_number, whichBuilding=building)
            except ObjectDoesNotExist:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f" شقة رقم '{apartment_number}' غير موجودة في عمارة '{building_number}'."
                })

            try:
                casualty = Group.objects.get(groupName=casualty)
            except ObjectDoesNotExist:
                return render(request, 'operations/uploade_excel_for_person.html', {
                    "errorMessage": f" المصاب '{casualty}' غير مسجل لدينا. تأكد من كتابته بشكل صحيح مطابق للمصابين في قواعد البيانات"
                })

            # Check if person with the same ID number already exists
            if Person.objects.filter(idNumber=id_number).exists():
                continue  # Skip this row if ID number already exists
            person = Person(
                name=name,
                birthday=birthday,
                theType='مرافق',
                idNumber=id_number,
                gender=gender,
                diagnosis=diagnosis,
                personGroup=casualty,
                pHospital=hospital,
                accommodation=apartment,
                status=status,
                phoneNumber=phoneNumber,
                entryDate=entryDate,
                hostingStartDate=hostingStartDate
            )
            person.save()

        return render(request, 'operations/uploade_excel_for_person.html', {
            "message": "تم إضافة المستفيدين بنجاح!"
        })

    return render(request, 'operations/uploade_excel_for_person.html')




# Add person
@login_required
def addPerson(request):
    if request.method == "GET":    
        return render(request, 'operations/addperson.html', {
            "users" : User.objects.all(),
            "Group" : Group.objects.all(),
            "Hospitals": Hospital.objects.all(),
            "Apartments": Apartment.objects.all(),

        })
    else:
        # Handle the POST date
        name = request.POST["name"]
        idNumber = request.POST["idNumber"]
        birthday = request.POST["birthday"]
        entrydate = request.POST["entrydate"]
        hostingStartDate = request.POST["hostingStartDate"]
        theType = request.POST["theType"]
        gender = request.POST["gender"]
        status = request.POST["status"]
        phoneNumber = request.POST["phoneNumber"]
        GroupName = request.POST["Group"]
        HospitalName = request.POST["Hospital"]
        Apartmente = request.POST["Apartment"]
        diagnosis = request.POST["diagnosis"]
        hasCancer = request.POST.get("hasCancer", False)
        isDisabled = request.POST.get("isDisabled", False)
        profilePic = request.FILES.get("profilePic", False)
        uploadedfile = request.FILES.get("uploadedfile", False)

        # Check if the person exists in the DB
        personExists = Person.objects.filter(idNumber = idNumber)
        if personExists:
            return render(request, "operations/addperson.html", {
                "errorMessage" : "Error",
                "personName" : name,
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })
        # Get the instance of 
        groupInst = Group.objects.get(id = GroupName)
        hosptialInst = Hospital.objects.get(id = HospitalName)
        apartmentInst = Apartment.objects.get(id = Apartmente)
        
        if hasCancer == 'True':
            hasCancer = True
        else:
            hasCancer = False

        if isDisabled == 'True':
            isDisabled = True
        else:
            isDisabled = False

        # Inserting the date into the database
        theperson = Person.objects.create(
            name = name,
            personGroup = groupInst,
            birthday = birthday,
            theType = theType,
            gender = gender,
            idNumber = idNumber,
            status = status, 
            phoneNumber = phoneNumber,
            diagnosis = diagnosis,
            pHospital = hosptialInst,
            accommodation = apartmentInst,
            scannedDocs = uploadedfile,
            profile_pic = profilePic,
            hasCancer = hasCancer,
            isDisabled = isDisabled,
            entryDate = entrydate,
            hostingStartDate = hostingStartDate,

        )
        return render(request, "operations/addperson.html", {
                "message" : "تم إضافة المستفيد بنجاح!",
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })     

@login_required
def addCasualty(request):
    if request.method == "GET":    
        return render(request, 'operations/addcasualty.html', {
            "users" : User.objects.all(),
            "Hospitals": Hospital.objects.all(),
            "Apartments": Apartment.objects.all(),
        })
    else:
        # Handle the POST date
        name = request.POST["name"]
        # Check this value is not empty
        if not name:
                return render(request, 'operations/addcasualty.html', {
                    "errorMessage": "خانة اسم المصاب خانة إلزامية",
                    "users" : User.objects.all(),
                    "Hospitals": Hospital.objects.all(),
                    "Apartments": Apartment.objects.all(),
                })
        idNumber = request.POST["idNumber"]
        # Check this value is not empty
        if not idNumber:
                return render(request, 'operations/addcasualty.html', {
                    "errorMessage": "خانة رقم هوية المصاب خانة إلزامية",
                    "users" : User.objects.all(),
                    "Hospitals": Hospital.objects.all(),
                    "Apartments": Apartment.objects.all(),                    
                })
        birthday = request.POST["birthday"]
        entrydate = request.POST["entrydate"]
        hostingStartDate = request.POST["hostingStartDate"]
        theType = 'مصاب '
        gender = request.POST.get("gender", None)
        # Check this value is not empty
        if not gender:
                return render(request, 'operations/addcasualty.html', {
                    "errorMessage": "برجاء ادخال نوع المصاب",
                    "users" : User.objects.all(),
                    "Hospitals": Hospital.objects.all(),
                    "Apartments": Apartment.objects.all(),                    
                })
        status = request.POST.get("status", None)
        # Check this value is not empty
        if not status:
                return render(request, 'operations/addcasualty.html', {
                    "errorMessage": "يرجى اختيار الوضع الحالي للمصاب",
                    "users" : User.objects.all(),
                    "Hospitals": Hospital.objects.all(),
                    "Apartments": Apartment.objects.all(),                    
                })
        phoneNumber = request.POST["phoneNumber"]
        GroupName = request.POST["name"]
        HospitalName = request.POST.get("Hospital", None)
        if not HospitalName:
                return render(request, 'operations/addcasualty.html', {
                    "errorMessage": "برجاء اختيار اسم المستشفى القادم منه المصاب",
                    "users" : User.objects.all(),
                    "Hospitals": Hospital.objects.all(),
                    "Apartments": Apartment.objects.all(),
                })
        Apartmente =request.POST.get("Apartment", None)
        if not Apartmente:
                return render(request, 'operations/addcasualty.html', {
                    "errorMessage": "برجاء اختيار الشقة التي سيقيم المصاب فيها",
                    "users" : User.objects.all(),
                    "Hospitals": Hospital.objects.all(),
                    "Apartments": Apartment.objects.all(),
                })
        diagnosis = request.POST["diagnosis"]
        hasCancer = request.POST.get("hasCancer", False)
        isDisabled = request.POST.get("isDisabled", False)
        profilePic = request.FILES.get("profilePic", False)
        uploadedfile = request.FILES.get("uploadedfile", False)
   
        # Inserting the date into the database

        # Making sure the group doesn't exist already
        groupExists = Group.objects.filter(groupName = name)
        if groupExists:
            return render(request, "operations/addcasualty.html", {
                "errorMessage" : f"المصاب {name} موجود بالفعل في قواعد البيانات",
                "personName" : name,
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })
        # Check if the person exists in the DB
        personExists = Person.objects.filter(idNumber = idNumber)
        if personExists:
            return render(request, "operations/addcasualty.html", {
                "errorMessage" : f"المصاب {name} موجود بالفعل في قواعد البيانات",
                "personName" : name,
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })


        try:
            hosptialInst = Hospital.objects.get(id = HospitalName)
        except ObjectDoesNotExist:
            return render(request, 'operations/addcasualty.html', {
                "errorMessage": "حدث خطأ عند اختيار المستشفى, برجاء المحاولة مجددًا",
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),
            })

        try:
            apartmentInst = Apartment.objects.get(id = Apartmente)
        except ObjectDoesNotExist:
            return render(request, 'operations/addcasualty.html', {
                "errorMessage": "حدث خطأ عند اختيار مكان الاقامة, برجاء المحاولة مجددًا",
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),
            })


        
        theGroup = Group.objects.create(
            groupName = name
        )

        groupInst = Group.objects.get(groupName = name)

        if hasCancer == 'True':
            hasCancer = True
        else:
            hasCancer = False

        if isDisabled == 'True':
            isDisabled = True
        else:
            isDisabled = False


        theperson = Person.objects.create(
            name = name,
            personGroup = groupInst,
            birthday = birthday,
            theType = theType,
            idNumber = idNumber,
            status = status, 
            gender = gender,
            phoneNumber = phoneNumber,
            diagnosis = diagnosis,
            pHospital = hosptialInst,
            accommodation = apartmentInst,
            scannedDocs = uploadedfile,
            profile_pic = profilePic,
            hasCancer = hasCancer,
            isDisabled = isDisabled,
            entryDate = entrydate,
            hostingStartDate = hostingStartDate,

        )

        return render(request, "operations/addcasualty.html", {
                "message" : "تم إضافة المستفيد بنجاح!",
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })    

@login_required
def accommodation(request):    
    if request.method == "GET":
        return render(request, 'operations/accommodation.html', {
            "users": User.objects.all(),
            "Person": Person.objects.all(),
            "Apartments": Apartment.objects.all(),
        })
    else:
        # Handle the POST data
        person_ids = request.POST.getlist("names[]")
        apartment_id = request.POST["Apartment"]
        apartment_instance = Apartment.objects.get(id=apartment_id)
        
        # Update accommodation for each selected person
        for person_id in person_ids:
            Person.objects.filter(id=person_id).update(accommodation=apartment_instance, status = "داخل السكن")
        
        # Get updated persons and the apartment instance for the context
        updated_persons = Person.objects.filter(id__in=person_ids)
        
        return render(request, "operations/accommodation.html", {
            "message": "تم إضافة المستفيدين بنجاح!",
            "users": User.objects.all(),
            "Person": Person.objects.all(),
            "Apartments": Apartment.objects.all(),
            "updated_persons": updated_persons,
            "theApartment": apartment_instance,
        })


@login_required
def customers(request):
    query = request.GET.get('q', '')
    whichCases = request.GET.get('whichCases', '')

    customersList = Person.objects.all()

    if query:
        customersList = customersList.filter(
            Q(name__icontains=query) |
            Q(idNumber__icontains=query) |
            Q(phoneNumber__icontains=query) |
            Q(diagnosis__icontains=query)
        )

    if whichCases:
        if whichCases == '0':
            customersList = customersList.filter(status='داخل السكن')
        elif whichCases == '1':
            two_years_ago = datetime.now() - timedelta(days=2*365)
            customersList = customersList.filter(birthday__gte=two_years_ago)
        elif whichCases == '2':
            customersList = customersList.filter(Q(gender='انثى') | Q(gender='أنثى'))
        elif whichCases == '3':
            customersList = customersList.filter(gender='ذكر')
        elif whichCases == '4':
            customersList = customersList.filter(hasCancer=True)
        elif whichCases == '5':
            customersList = customersList.filter(isDisabled=True)

    paginator = Paginator(customersList, 100)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        customers = paginator.page(page)
    except (EmptyPage, InvalidPage):
        customers = paginator.page(paginator.num_pages)

    return render(request, "operations/customers.html", {
        "customers": customers,
        "query": query,
        "whichCases": whichCases
    })

@login_required
def sheltersStat(request):
    # Get all shelter instances
    shelters = Shelter.objects.all()
    shelter_data = []

    # Iterate through each shelter to calculate statistics
    for shelter in shelters:
        buildings = shelter.Buildings.all()  # Get all buildings related to the shelter
        total_capacity = 0
        total_residents = 0

        # Iterate through each building to calculate total capacity and residents
        for building in buildings:
            apartments = building.apartments.all()  # Get all apartments related to the building
            for apartment in apartments:
                total_capacity += apartment.apartmentCapacity  # Sum the capacity of all apartments
                total_residents += apartment.residents.filter(status="داخل السكن").count()  # Sum the residents in all apartments

        # Calculate available spots for new guests
        available_spots = total_capacity - total_residents

        # Append shelter data to the list
        shelter_data.append({
            'id': shelter.id,
            'shelter_name': shelter.shelterName,
            'total_capacity': total_capacity,
            'total_residents': total_residents,
            'available_spots': available_spots  # Add available spots for new guests
        })

    # Pass the shelter data to the context for rendering in the template
    context = {'shelter_data': shelter_data}
    return render(request, 'operations/shelters.html', context)


@login_required
def shelterDetails(request, shelter_id):

    # Get the shelter instance based on the ID
    shelter = get_object_or_404(Shelter, id=shelter_id)
    buildings = shelter.Buildings.all()  # Get all buildings related to the shelter

    apartment_data = []

    # Iterate through each building to gather apartment details
    for building in buildings:
        apartments = building.apartments.all()  # Get all apartments related to the building
        for apartment in apartments:
            residents = apartment.residents.filter(status="داخل السكن")  # Get all residents in the apartment
            resident_names = [{'name': resident.name, 'id': resident.id} for resident in residents]
            available_spots = apartment.apartmentCapacity - len(residents)

            apartment_data.append({
                'id': shelter.id,
                'apartment_name': apartment,
                'capacity': apartment.apartmentCapacity,
                'residents': resident_names,
                'available_spots': available_spots
            })

    context = {
        'shelter_name': shelter.shelterName,
        'apartment_data': apartment_data,
        'shelter_id': shelter.id,
    }
    return render(request, 'operations/apartment_details.html', context)

@login_required
def availableApartments(request, shelter_id):
    # Get the shelter instance based on the ID
    shelter = get_object_or_404(Shelter, id=shelter_id)
    buildings = shelter.Buildings.all()  # Get all buildings related to the shelter

    apartment_data = []

    # Iterate through each building to gather apartment details
    for building in buildings:

        

        # Filter apartments in the building where the count of residents is less than the capacity
        apartments_with_available_spots = building.apartments.annotate(
        num_residents_with_status=Count('residents', filter=models.Q(residents__status='داخل السكن'))
        ).filter(num_residents_with_status__lt=models.F('apartmentCapacity'))




        for apartment in   apartments_with_available_spots:
            residents = apartment.residents.filter(status="داخل السكن")  # Get all residents in the apartment
            resident_names = [{'name': resident.name, 'id': resident.id} for resident in residents]
            available_spots = apartment.apartmentCapacity - len(residents)

            apartment_data.append({
                'apartment_name': apartment,
                'capacity': apartment.apartmentCapacity,
                'residents': resident_names,
                'available_spots': available_spots
            })

    context = {
        'shelter_name': shelter.shelterName,
        'apartment_data': apartment_data
    }
    return render(request, 'operations/apartments_with_available_spots.html', context)


@login_required
def profile(request, person_id):

    # Get the person instance based on the ID
    person = get_object_or_404(Person, id=person_id)
    
    # Get the relatives of the person
    relatives = person.personGroup.relatives.exclude(id=person_id)

    # Get the diseases the person is affected by
    diseases = AffectedBy.objects.filter(person=person)

    # Get the ambulance_log of the person
    ambulance = ambulance_log.objects.filter(casualty = person)

    # Get the docs of the person
    UploadedDocuments = UploadedDocument.objects.filter(person = person)


    context = {
        'person': person,
        'relatives': relatives,
        'diseases': diseases,
        'ambulances': ambulance,
        'UploadedDocuments':UploadedDocuments,
        
    }
    return render(request, 'operations/profile.html', context)

@login_required
def removePerson(request):
    if request.method == "GET":
        return render(request, 'operations/remove_person.html', {
            "Person": Person.objects.all()
        })
    else:
        # Handle the POST data
        person_ids = request.POST.getlist("names[]")
        date = request.POST["thedate"]
        status = request.POST["status"]
        uploadedfile = request.FILES.get("uploadedfile", False)
        # Update accommodation for each selected person
        for person_id in person_ids:
            logOutLogs.objects.create(
                date = date,
                person = Person.objects.get(id=person_id),
                scannedDocs = uploadedfile
            )
            Person.objects.filter(id=person_id).update(status=status)
            
        
        # Get updated persons and the apartment instance for the context
        updated_persons = Person.objects.filter(id__in=person_ids)

        return render(request, "operations/remove_person.html", {
            "message": "تم تسجيل خروج المستفيدين بنجاح!",
            "Person": Person.objects.all(),
            "updated_persons": updated_persons,
        })



@login_required
def customersOut(request):
    customersList = Person.objects.exclude(status = "داخل السكن")
    paginator = Paginator(customersList, 30) 
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1    

    try:
        customers = paginator.page(page)
    except(EmptyPage, InvalidPage):
        customers = paginator.page(paginator.num_pages)
    return render(request, "operations/removed_persons.html", {
        "customers" : customers,
        "logOutLogs": logOutLogs.objects.all()
    })



# def extract_id_number(image_path):
#     # Use pytesseract to do OCR on the image
#     text = pytesseract.image_to_string(Image.open(image_path))

#     # Use regex to find all sequences of exactly 9 digits, ignoring spaces
#     potential_ids = re.findall(r'\b\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\s*\d\b', text)

#     # Remove spaces from the extracted numbers
#     potential_ids = [id_number.replace(' ', '') for id_number in potential_ids]

#     # Filter the list to find IDs that start with 9, 8, or 4
#     valid_ids = [id_number for id_number in potential_ids if id_number.startswith(('9', '8', '4'))]

#     return valid_ids    

# @login_required
# def upload_document(request):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         files = request.FILES.getlist('document')
#         if form.is_valid() and files:
#             associated_persons = []
#             extracted_ids = []
#             temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
#             os.makedirs(temp_dir, exist_ok=True)
#             for f in files:
#                 # Save the file to a temporary location
#                 temp_file_path = os.path.join(temp_dir, f.name)
#                 with open(temp_file_path, 'wb+') as temp_file:
#                     for chunk in f.chunks():
#                         temp_file.write(chunk)
                
#                 id_numbers = extract_id_number(temp_file_path)
                
#                 if id_numbers:
#                     unique_id_numbers = set(id_numbers)
#                     with transaction.atomic():
#                         for id_number in unique_id_numbers:
#                             try:
#                                 person = Person.objects.get(idNumber=id_number)
#                                 if not UploadedDocument.objects.filter(document=f, person=person).exists():
#                                     # Save the file permanently associated with the person
#                                     uploaded_document = UploadedDocument(document=f, person=person, id_number=id_number)
#                                     uploaded_document.save()
#                                     associated_persons.append(person)
#                             except Person.DoesNotExist:
#                                 extracted_ids.append(f"{id_number} (اسم الملف: {f.name})")
                
#                 # Remove the temporary file
#                 os.remove(temp_file_path)
            
#             # حذف المستندات الغير مسندة إلى أي شخص
#             UploadedDocument.objects.filter(person__isnull=True).delete()
            
#             if associated_persons:
#                 return render(request, 'operations/upload.html', {
#                     'form': form,
#                     'message': "الملف الذي تم رفعه مسند إلى الأشخاص:",
#                     'persons': associated_persons,
#                     'error_message': f"لا يوجد اشخاص يحملوا أرقام الهويات الآتية:" if extracted_ids else None,
#                     'wrongID' : extracted_ids
#                 })
#             else:
#                 return render(request, 'operations/upload.html', {
#                     'form': form,
#                     'error_message': f"لا يوجد اشخاص يحملوا أرقام الهويات الآتية:",
#                     'wrongID' : extracted_ids
#                 })
#         else:
#             return render(request, 'operations/upload.html', {
#                 'form': form,
#                 'error_message': "ملف غير مدعم او لا يوجد ملفات تم رفعها"
#             })
#     else:
#         form = DocumentForm()
#     return render(request, 'operations/upload.html', {'form': form})


@login_required
def ManualUploadDocument(request):
    if request.method == 'GET':
        return render(request, 'operations/manual_upload.html', {'Persons': Person.objects.all()})

    elif request.method == 'POST' and request.FILES:
        # Handle the POST data
        person_ids = request.POST.getlist("names[]")
        uploaded_files = request.FILES.getlist("document")

        # Update accommodation for each selected person
        for person_id in person_ids:
            person = Person.objects.get(id=person_id)
            for uploaded_file in uploaded_files:
                UploadedDocument.objects.create(
                    person=person,
                    document=uploaded_file,
                    title=uploaded_file.name  # Ensure title is set to file name
                )

        return render(request, "operations/manual_upload.html", {
            "message": "تم رفع المستندات بنجاح",
            "Persons": Person.objects.all(),
        })
