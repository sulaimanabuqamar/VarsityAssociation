from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from basketball.models import *
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, FloatField, IntegerField
from django.http import HttpResponse


def home(request):
    page_data = LandingPage.objects.all()
    return render(request, "base/LandingPage.html", {'title': 'Home', 'page_data': page_data})

# used logoutUser since logout function is built function


def logoutUser(request):
    logout(request)
    return redirect('home')




