from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from django.contrib.auth import authenticate

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="密码")

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="用户名",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("用户名或密码错误")
        return cleaned_data