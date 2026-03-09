from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, GalleryImage, SoilTestRequest, AIReport, District


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email or Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email or Phone Number',
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'id_password',
        })
    )


import uuid

class FarmerRegisterForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.filter(is_active=True),
        required=True,
        empty_label="Select District",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        password_confirm = cleaned_data.get('password2')
        if password and password_confirm and password != password_confirm:
            self.add_error('password2', "Passwords don't match")
        
        email = cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', "A user with that email already exists.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate a unique username since it's not exposed to the user
        user.username = str(uuid.uuid4())[:30]
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role='farmer',
                phone=self.cleaned_data.get('phone', ''),
                district=self.cleaned_data.get('district'),
            )
        return user


class AIReportForm(forms.Form):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': 'image/*',
            'id': 'plant-image-upload',
        }),
        help_text='Upload a clear image of the cardamom plant or pods for analysis'
    )


class SoilTestRequestForm(forms.ModelForm):
    class Meta:
        model = SoilTestRequest
        fields = ['farm_location', 'farm_size', 'soil_type', 'additional_info']
        widgets = {
            'farm_location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your farm location / village / district'
            }),
            'farm_size': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Farm size in acres',
                'step': '0.1'
            }),
            'soil_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Clay / Sandy / Loamy / Red / Black (optional)'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Any additional information about your soil or farm...',
                'rows': 4
            }),
        }


class GalleryUploadForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'image', 'caption', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Image title'}),
            'caption': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Caption'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
        }


class AdminSoilUpdateForm(forms.ModelForm):
    class Meta:
        model = SoilTestRequest
        fields = ['status', 'admin_notes', 'scheduled_date']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Add notes for the farmer...'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
        }


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'District Name'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

