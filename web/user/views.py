# user/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .form import SignUpForm
from django.urls import reverse_lazy

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)  
            return redirect('home')  
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})
