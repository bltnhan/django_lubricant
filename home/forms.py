from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Người dùng không có trong CSDL')
            if not user.check_password(password):
                raise forms.ValidationError('Mật khẩu không khớp')
            if not user.is_active:
                raise forms.ValidationError('Người dùng chưa được kích hoạt....')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Nhập email")
    email2 = forms.EmailField(label="Xác nhận email")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'email2', 'password']

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')

        if email != email2:
            raise forms.ValidationError('Email không khớp')
        email_q = User.objects.filter(email=email)
        if email_q.exists():
            raise forms.ValidationError('Email đã có người dùng')
        return super(UserRegisterForm, self).clean(*args, **kwargs)