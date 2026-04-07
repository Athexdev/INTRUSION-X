from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Place for future custom user views (e.g. Profile or Registration)
def register(request):
    # This is a placeholder for future expansion
    return redirect('login')

@login_required
def debesh(request):
    return HttpResponse("System Developed by Debesh",)
