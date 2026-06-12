from django import forms
from .models import Address,UserProfile
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class AccountForm(UserChangeForm):
    first_name=forms.CharField(max_length=255,widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name=forms.CharField(max_length=255,widget=forms.TextInput(attrs={'class':'form-control'}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    username=forms.CharField(max_length=255,widget=forms.TextInput(attrs={'class':'form-control'}))
    class Meta:
        model= User
        fields=('first_name','last_name','username','email')
       
class ProfileForm(forms.ModelForm):
    indian_phone_regex = RegexValidator(
    regex=r'^(\+91|0)?[6-9]\d{9}$',
    message="Please enter a valid Indian Phone Number.")
       
    phone_number = forms.CharField(
    validators=[indian_phone_regex],max_length=15, # Allow extra space for +91
    widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Phone Number'}))

    class Meta:
        model = UserProfile
        # List the fields you want to show in the form
        fields = [ 'phone_number','gender','dob','city']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your City'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'type':'date','class': 'form-control'}),

        }


class AddressForm(forms.ModelForm):
    # Adding a phone number field with validation
    indian_phone_regex = RegexValidator(
    regex=r'^(\+91|0)?[6-9]\d{9}$',
    message="Please enter a valid Indian phone number.")
       
    phone_number = forms.CharField(
    validators=[indian_phone_regex],max_length=15, # Allow extra space for +91
    widget=forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0','placeholder': '9876543210'}))
    class Meta:
        model  = Address
        #List the fields you want to show in the form
        fields = ['full_name','phone_number','street_address',
                  'city','state','postal_code','country',
                  'address_type','is_default'
                  ]

        #Add CSS classes and placeholders for better UI
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'Full Name'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'House No, Street, Colony'}),
            'city': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'Zip/Pin Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'Country'}),
            'address_type': forms.Select(attrs={'class': 'form-select bg-theme-light p-3 border-0'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input border border-dark'}),
        }