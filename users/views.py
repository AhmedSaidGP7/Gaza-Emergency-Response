from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
# Create your views here.

# The view that handles authentication
def auth(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:index"))
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("users:index"))
        else:
            return render(request, "users/login.html", {
                "message": "برجاء التأكد من اسم المستخدم وكلمة المرور "
            })
    else:
        return render(request, "users/login.html")

# The view that handles singing out 
def signout(request):
    logout(request)
    return render(request, "users/login.html")

# The view that renders the homepage
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))
    return render(request, "users/index.html")