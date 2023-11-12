from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Site
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+\d{1,15}$',
    message="Phone number must start with '+' and contain only digits."
)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': '+380XXXXXXXXX'}),
        validators=[phone_validator]

    )
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'phone']


class UserLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
    )

    class Meta:
        model = User
        fields = ['username', 'password']


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'url']

