from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
import datetime
from GazaResponse.models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta




# Add person
@login_required(login_url="/auth")
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
            isDisabled = isDisabled

        )
        return render(request, "operations/addperson.html", {
                "message" : "تم إضافة المستفيد بنجاح!",
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })     

@login_required(login_url="/auth")
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
        idNumber = request.POST["idNumber"]
        birthday = request.POST["birthday"]
        theType = 'مصاب '
        gender = request.POST["gender"]
        status = request.POST["status"]
        phoneNumber = request.POST["phoneNumber"]
        GroupName = request.POST["name"]
        HospitalName = request.POST["Hospital"]
        Apartmente = request.POST["Apartment"]
        diagnosis = request.POST["diagnosis"]
        hasCancer = request.POST.get("hasCancer", False)
        isDisabled = request.POST.get("isDisabled", False)
        profilePic = request.FILES.get("profilePic", False)
        uploadedfile = request.FILES.get("uploadedfile", False)
   
        # Inserting the date into the database
        groupExists = Group.objects.filter(groupName = name)
        if groupExists:
            return render(request, "operations/addcasualty.html", {
                "errorMessage" : "Error",
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
                "errorMessage" : "Error",
                "personName" : name,
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })

        theGroup = Group.objects.create(
            groupName = name
        )

        groupInst = Group.objects.get(groupName = name)
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
            isDisabled = isDisabled

        )

        return render(request, "operations/addcasualty.html", {
                "message" : "تم إضافة المستفيد بنجاح!",
                "users" : User.objects.all(),
                "Group" : Group.objects.all(),
                "Hospitals": Hospital.objects.all(),
                "Apartments": Apartment.objects.all(),

            })    

@login_required(login_url="/auth")
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
            Person.objects.filter(id=person_id).update(accommodation=apartment_instance)
        
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


@login_required(login_url="/auth")
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
            customersList = customersList.filter(gender='انثى')
        elif whichCases == '3':
            customersList = customersList.filter(gender='ذكر')
        elif whichCases == '4':
            customersList = customersList.filter(hasCancer=True)
        elif whichCases == '5':
            customersList = customersList.filter(isDisabled=True)

    paginator = Paginator(customersList, 30)
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

@login_required(login_url="/auth")
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


@login_required(login_url="/auth")
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

@login_required(login_url="/auth")
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


@login_required(login_url="/auth")
def profile(request, person_id):

    # Get the person instance based on the ID
    person = get_object_or_404(Person, id=person_id)
    
    # Get the relatives of the person
    relatives = person.personGroup.relatives.exclude(id=person_id)

    context = {
        'person': person,
        'relatives': relatives
    }
    return render(request, 'operations/profile.html', context)

@login_required(login_url="/auth")
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

@login_required(login_url="/auth")
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