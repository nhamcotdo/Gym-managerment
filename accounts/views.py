from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages

# from accounts.forms import PasswordChangeFormCustom
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm



def homepage_after_login(request):
    return render(request, 'base.html')

def loginCustom(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        
        next = request.GET.get('next', '')
        return render(request, 'accounts/login.html', {'next': next})
    
    elif request.method == 'POST':
        next = request.POST.get('next', '')
        if request.user.is_authenticated:
            return redirect(next or '/')
        
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect(next or '/')
            else:
                return render(request, 'accounts/login.html', {'error': 'Tên đăng nhập hoặc mật khẩu không chính xác!'})
        else:
            return render(request, 'accounts/login.html', {'form': form, 'error': 'Tên đăng nhập hoặc mật khẩu không chính xác!'})

def logout_view(request):
    logout(request)
    return redirect('login')

def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            return render(request, 'accounts/password_change_success.html')
    
    if request.method == 'GET':
        form = PasswordChangeForm(request.user)

    context = {'form': form}
    return render(request, 'accounts/password_change.html', context)
