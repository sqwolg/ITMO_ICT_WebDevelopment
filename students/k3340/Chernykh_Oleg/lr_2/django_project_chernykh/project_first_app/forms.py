from django import forms
from django.contrib.auth.models import User
from .models import Owner, Car


class UserOwnerForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    
    class Meta:
        model = Owner
        fields = ['passport_number', 'address', 'nationality', 'birth_date']
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data.get('email', '')
        )
        owner = Owner.objects.create(
            user=user,
            passport_number=self.cleaned_data['passport_number'],
            address=self.cleaned_data['address'],
            nationality=self.cleaned_data['nationality'],
            birth_date=self.cleaned_data['birth_date']
        )
        return owner


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['passport_number', 'address', 'nationality', 'birth_date']


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'brand', 'model', 'color']

