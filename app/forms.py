from django import forms
from .models import Contact
from django.core.validators import RegexValidator

class ContactForm(forms.ModelForm):
    # Adding a phone number field with validation
    indian_phone_regex = RegexValidator(
    regex=r'^(\+91|0)?[6-9]\d{9}$',
    message="Please enter a valid Indian phone number.")
       
    phone_number = forms.CharField(
    validators=[indian_phone_regex],max_length=15, # Allow extra space for +91
    widget=forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0','placeholder': '9876543210'}))
    class Meta:
        model  = Contact
        #List the fields you want to show in the form
        fields = ['name','email','phone_number','message']

        #Add CSS classes and placeholders for better UI
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'placeholder':'name@example.com'}),
            'message': forms.Textarea(attrs={'class': 'form-control bg-theme-light p-3 border-0', 'rows':4, 'placeholder':'Your Message'})
        }