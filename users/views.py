from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from .forms import UserRegisterForm, LoginForm
from .models import User, StudentProfile, InstructorProfile

# Create your views here.


def signup(request):

    if request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            role = form.cleaned_data["role"]

            if role == "student":
                user.is_student = True
            else:
                user.is_instructor = True

            user.save()

            if user.is_student:
                StudentProfile.objects.create(user=user)

            if user.is_instructor:
                InstructorProfile.objects.create(user=user)

            login(request, user)

            return redirect("index")

    else:
        form = UserRegisterForm()

    return render(request, "sign-up.html", {
        "form": form
    })



def signin(request):

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            login(request, form.get_user())

            return redirect("home")

    return render(request, "sign-in.html", {
        "form": form
    })


def logout_view(request):
    logout(request)
    return redirect("login")