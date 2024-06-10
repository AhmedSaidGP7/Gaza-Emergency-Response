from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from GazaResponse.models import *
from .models import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponseRedirect  


# Create your views here.
@login_required(login_url="/auth")
def addPost(request):
    if request.method == "GET":
        return render(request, 'cases/add_post.html', {
            "Persons": Person.objects.all(),

        })
    else:
        # Handle the POST request
        title = request.POST["title"]
        belongsTo = request.POST["thename"]
        status = "New"
        content = request.POST["content"]
        ticketScannedDocs = request.FILES.get("uploadedfile", False)
        if request.POST["theType"] == "True":
            is_urgent = True
        else:
            is_urgent = False

        getPersonInstance = Person.objects.get(id = belongsTo)
        user = request.user
        TheTicket = Tickets.objects.create(
            title = title,
            belongsTo = getPersonInstance,
            is_urgent = is_urgent,
            content = content,
            ticketScannedDocs = ticketScannedDocs,
            author= user,  
            caseResponsible= user,
            status = status
        )
        return render(request, "cases/add_post.html", {
                "message" : "تم إضافة المستفيد بنجاح!",
                "Persons": Person.objects.all(),

            }) 

@login_required(login_url="/auth")
def retrieveAllPosts(request):
    return render(request, "cases/all_posts.html", {
        "persons": Person.objects.all(),
        "tickets": Tickets.objects.all(),
        "users": User.objects.all()
    })


@login_required(login_url="/auth")
def retrieveSomePosts(request):
    whichCases = request.POST["whichCases"]
    cases = []
    if whichCases == '1':
        cases = Tickets.objects.filter(status = "New")
    elif whichCases == '2':
        cases = Tickets.objects.filter(status = "Ongoing")
    elif whichCases == '3':
        cases = Tickets.objects.filter(status = "Closed")
    elif whichCases == '0':
        cases = Tickets.objects.all()
    return render(request, "cases/all_posts.html", {
        "persons": Person.objects.all(),
        "tickets": cases,
        "users": User.objects.all()
    })


@login_required(login_url="/auth")
def serachPost(request):
    query = request.GET.get('query', '')
    results = Tickets.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(belongsTo__idNumber__icontains=query) |
                Q(belongsTo__name__icontains=query) |
                Q(belongsTo__phoneNumber__icontains = query)
            )   
    return render(request, "cases/all_posts.html", {
        "persons": Person.objects.all(),
        "tickets": results,
        "users": User.objects.all()
    })




@login_required(login_url="/auth")
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    return render(request, 'cases/ticket_detail.html', {
        'ticket': ticket,
        "persons": Person.objects.all(),
        "users": User.objects.all(),
        "comments": comments.objects.filter(ticket = ticket)
    })


@login_required(login_url="/auth")
def CloseCase(request):
    caseID =  request.POST.get("caseID")
    case = get_object_or_404(Tickets, id=caseID)
    case.status = 'Closed'
    case.save()
    return HttpResponseRedirect(reverse('case_management:cases'))

@login_required(login_url="/auth")
def addComment(request):
    caseID = request.POST.get("theticket")
    comment = request.POST.get("comment")
    user = request.user
    case = get_object_or_404(Tickets, id=caseID)
    newComment = comments.objects.create(
        author= user,
        content = comment,
        ticket = case
    )
    case.status = 'Ongoing'
    case.save()
    return HttpResponseRedirect(reverse('case_management:cases'))
