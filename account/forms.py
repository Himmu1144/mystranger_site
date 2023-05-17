from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import Account
from django.contrib.auth import authenticate


class RegistrationForm(UserCreationForm):

    email = forms.EmailField(max_length=255,help_text='Enter a Valid Email.')

    class Meta:
        model = Account
        fields = ('email','password1','password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        college_email = email.split('.')[-2:]
        if not (college_email == ['edu', 'in']):
            raise forms.ValidationError(f'Email must ends with .edu.in')
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email - {email} is already in use.')

    def save(self, commit=True):
        account = super(RegistrationForm, self).save(commit=False)
        email = self.cleaned_data['email'].lower()
        account.name = email.split('.')[0].capitalize()
        account.email = self.cleaned_data['email'].lower()
        account.university_name = email.split('@')[-1:][0]
        if commit:
            account.save()
        return account

class AccountAuthenticationForm(forms.ModelForm):
    email = forms.EmailField(max_length=255,label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        college_email = email.split('.')[-2:]
        if not (college_email == ['edu', 'in']):
            raise forms.ValidationError(f'Email must ends with .edu.in')
        try:
            account = Account.objects.get(email=email)
            return email
        except Account.DoesNotExist:
            raise forms.ValidationError(f'Account with Email - {email} - does not exist!')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email,password=password):
                raise forms.ValidationError("Invalid Credentials!")