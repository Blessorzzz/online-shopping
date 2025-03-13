# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .form import SignUpForm

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # 使用默认的 commit=True
            print(f"User saved: {user.username}, Profile address: {user.userprofile.address}")  # 调试
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)  # 如果表单无效，打印错误
            return render(request, 'register.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})
