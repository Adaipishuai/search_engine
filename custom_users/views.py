from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, UserLoginForm
from custom_users.models import SearchHistory
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('search_index:index')
    else:
        form = UserRegistrationForm()
    return render(request, 'custom_users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('search_index:index')
    else:
        form = UserLoginForm()
    return render(request, 'custom_users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('search_index:index')




