from django.contrib.auth.models import User
from django import forms
from .models import video
class UserForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=User
        fields=['username','email','password']

class VideoForm(forms.ModelForm):

    class Meta:
        model=video
        fields=['videoname']