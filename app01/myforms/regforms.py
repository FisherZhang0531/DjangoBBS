""" Customized Forms"""

from django import forms
from django.core.validators import RegexValidator
from app01 import models


class RegForms(forms.Form):
    username = forms.CharField(
        label='username',
        min_length='8',
        validators=[
            RegexValidator(regex=r'[0-9]',message='Need at least one number'),
            RegexValidator(regex=r'\W',message='Need at least one symbol'),
            RegexValidator(regex=r'[a-z]',message='Need at least one lower letter'),
            RegexValidator(regex=r'[A-Z]',message='Need at least one upper letter'),
                    ],
        required=True,
        error_messages={
            'required': 'Username is Required Field',
            'min_length': "minimal need 8 letters"
        },
        widget=forms.widgets.TextInput(attrs={'class': 'col-sm-10 form-control'})
    )

    password = forms.CharField(
        label='password',
        min_length='8',
        required=True,
        validators=[RegexValidator],
        error_messages={
            'required': 'Password is Required',
            'min_length': 'The Password is minimal 8 letters',
        },
        widget=forms.widgets.PasswordInput(attrs={'class': 'col-sm-10 form-control'})
    )

    confirm_password = forms.CharField(
        label='confirm_password',
        min_length='8',
        required=True,
        validators='',
        error_messages={
            'required': 'Password is Required',
            'min_length': 'The Password is minimal 8 letters',
        },
        widget=forms.widgets.PasswordInput(attrs={'class': 'col-sm-10 form-control'})
    )

    email = forms.EmailField(
        label='email',
        error_messages={
            'required': 'Email is Required'
        },
        widget=forms.widgets.EmailInput(attrs={'class': 'col-sm-10 form-control'})
    )

    """hooks"""

    # check username in DB for existence check
    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_exist = models.User.objects.filter(username=username)
        if is_exist:
            self.add_error('username', 'User Already Exists')
        return username

    # check confirm password matches password
    def clean(self):
        pwd = self.cleaned_data.get('password')
        conf_pwd = self.cleaned_data.get('confirm_password')
        if not pwd == conf_pwd:
            self.add_error('confirm_password', 'Passwords not match')
        return self.cleaned_data
