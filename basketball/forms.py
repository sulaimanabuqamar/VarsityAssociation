from django import forms
from .models import Player
from .models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['team_name', 'team_abbreviation', 'team_logo',
                  'manager_first_name', 'manager_last_name', 'manager_phone_number', 'manager_email']
        widgets = {
            'team_name': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'School Name *'}),
            'team_abbreviation': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'Abbreviation *'}),
            'team_logo': forms.FileInput(attrs={"class": "file-input", "accept": "image/*", 'placeholder': 'Team logo *'}),
            'manager_first_name': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'First name *'}),
            'manager_last_name': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'Last name *'}),
            'manager_phone_number': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'Phone number *'}),
            'manager_email': forms.EmailInput(attrs={'class': 'form3', 'placeholder': 'Email Address *'}),
        }


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = ['player_first_name', 'player_last_name', 'player_date_of_birth',
                  'player_phone_number', 'player_email', 'player_image', 'player_shirt_number']

        widgets = {
            'player_first_name': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'First name *'}),
            'player_last_name': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'Last name'}),
            'player_date_of_birth': forms.DateInput(attrs={'class': 'form3', 'type': "text", 'onfocus': "(this.type='date')", 'onblur': "(this.type='text')", 'placeholder': 'Date of Birth'}),
            'player_phone_number': forms.TextInput(attrs={'class': 'form3', 'placeholder': 'Phone number'}),
            'player_email': forms.EmailInput(attrs={'class': 'form3', 'placeholder': 'Email address'}),
            'player_image': forms.FileInput(attrs={"class": "file-input", "accept": "image/*", 'placeholder': 'Player image'}),
            'player_shirt_number': forms.TextInput(attrs={'class': 'form3', 'type': 'number', 'placeholder': 'player shirt number *'}),
        }
