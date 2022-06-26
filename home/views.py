from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request, 'welcome.html', {})

def dashboard_1(request):
    return render(request, 'index1.html', {})

def update_data(request):
    return render(request, 'update_data.html', {})
def on_develope(request):
    return render(request, 'on_develope.html', {})

def dashboard_1_1(request):
    return render(request, 'index1_1.html', {})
def dashboard_2_1(request):
    return render(request, 'index2_1.html', {})

def dashboard_2_2(request):
    return render(request, 'index2_2.html', {})


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username,password=password)
        login(request, user)

        return redirect('/')
    else:
        HttpResponse('User này không tồn tại, vui lòng đăng nhập lại')
    return render(request,'accounts/login.html', {'form':form})

def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()

        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)

        return redirect('/')
    return render(request,'accounts/register.html', {'form':form})


def logout_view(request):
    logout(request)
    return redirect('/')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=data))
            if associated_user.exists():
                for user in associated_user:
                    subject = 'Password reset request'
                    email_template_name = 'accounts/email/password_reset_request.txt'
                    compose = {
                        'mail':user.email,
                        'domain':'127.0.0.1:7000',
                        'site_name':'mysite',
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)), #user.pk : ID (pk : primary key)
                        'token':default_token_generator.make_token(user),
                        'protocol':'http',
                    }
                    email = render_to_string(email_template_name, compose)
                    try:
                        send_mail(subject, email, 'aegis31032022@gmail.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid')
                    finally:
                        response = HttpResponse()
                        response.write('<p>A message with reset password instructions has been sent to your inbox.<p>')
                    return redirect("/")
            messages.error(request, 'An invalid email has been entered.')
    form = PasswordResetForm()
    return render(request,'accounts/password_reset_request.html', {'form':form})

def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html', {})

def password_reset_confirm(request):
    return render(request, 'accounts/password_reset_confirm.html, {}')

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html', {})

def notice_contact(request):
    return HttpResponse('<p>Please visit us at address: <i>7A/43/24 Thanh Thai, Ward 14, District 10, Ho Chi Minh City, Vietnam</i></p>')