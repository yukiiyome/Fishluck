from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FishingSpot, FishingTrip, Angler


class RegisterForm(UserCreationForm):
    region = forms.CharField(max_length=100, label='Регион')
    favorite_fish = forms.CharField(max_length=100, required=False, label='Любимая рыба')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'region', 'favorite_fish')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'


class FishingSpotForm(forms.ModelForm):
    class Meta:
        model = FishingSpot
        fields = ('name', 'spot_type', 'target_fish', 'notes')
        labels = {
            'name': 'Название',
            'spot_type': 'Тип водоёма',
            'target_fish': 'Целевая рыба',
            'notes': 'Заметки',
        }
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class FishingTripForm(forms.ModelForm):
    class Meta:
        model = FishingTrip
        fields = ('spot', 'date', 'water_temp', 'pressure', 'moon_phase', 'catch_weight_kg', 'fish_species', 'notes')
        labels = {
            'spot': 'Водоём',
            'date': 'Дата',
            'water_temp': 'Температура воды (°C)',
            'pressure': 'Давление (мм рт. ст.)',
            'moon_phase': 'Фаза луны',
            'catch_weight_kg': 'Вес улова (кг)',
            'fish_species': 'Виды рыбы',
            'notes': 'Заметки',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, angler=None, **kwargs):
        super().__init__(*args, **kwargs)
        if angler:
            self.fields['spot'].queryset = FishingSpot.objects.filter(angler=angler)

    def clean_water_temp(self):
        t = self.cleaned_data['water_temp']
        if t < -2 or t > 35:
            raise forms.ValidationError('Температура должна быть от -2 до 35°C')
        return t

    def clean_pressure(self):
        p = self.cleaned_data['pressure']
        if p < 700 or p > 800:
            raise forms.ValidationError('Давление должно быть от 700 до 800 мм рт. ст.')
        return p


class CalculatorForm(forms.Form):
    water_temp = forms.DecimalField(max_digits=4, decimal_places=1, label='Температура воды (°C)', min_value=-2, max_value=35)
    pressure = forms.IntegerField(label='Давление (мм рт. ст.)', min_value=700, max_value=800)
    moon_phase = forms.ChoiceField(choices=FishingTrip.MOON_PHASES, label='Фаза луны')