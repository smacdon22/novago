from django import forms
from django.core.exceptions import ValidationError
from .models import *
import datetime

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("profile_picture","first_name","last_name","profile_description")
        widgets = {'profile_picture' : forms.FileInput(attrs={"id": "file-input"})}


class SearchForm(forms.Form):
    where = forms.CharField(label='Where', max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Where', 'id': 'autocomplete', }))
    depart_date = forms.DateField(label='When', widget=forms.DateInput(
        attrs={'type': 'date'}), required=False)


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ('destination_address', 'starting_address',
                  'depart_date', 'depart_time', 'stops', 'passengers_amount', 'price')
        cur_datetime = datetime.datetime.now()
        cur_date = cur_datetime.date().strftime("%Y-%m-%d")
        widgets = {
            'starting_address': forms.TextInput(attrs={'class': 'textbox w-input',
                                                       'label': 'destination-address',
                                                       'placeholder': 'Starting Address',
                                                       'id': 'autocomplete1',
                                                       'name': 'destination_address', }),

            'destination_address': forms.TextInput(attrs={'class': 'textbox w-input',
                                                          'label': 'destination-address',
                                                          'placeholder': 'Destination Address',
                                                          'id': 'autocomplete',
                                                          'name': 'destination_address', }),
            'depart_date': forms.DateInput(attrs={'type': 'date', 'class': 'textbox w-input', 'min':cur_date}),
            'depart_time': forms.TimeInput(attrs={'type': 'time'}),
            'price': forms.NumberInput(attrs={'type': 'number', 'title':'Price per passenger', 'min':'0', 'max':'100'}),
            'passengers_amount': forms.NumberInput(attrs={'type': 'number', 'title':'Price per passenger', 'min':'0', 'max':'8'})
        }


class LoginForm(forms.Form):
    user = forms.EmailField(label='Email', required=True)
    password = forms.SlugField(label='Password', required=True, widget=forms.PasswordInput(
        attrs={'class': 'textbox w-input'}, render_value=False))


class FilterForm(forms.Form):
    location = forms.BooleanField(
        label="Filter by location", widget=forms.RadioSelect(choices=[('Exact', True)]))
    date = forms.BooleanField(label="Filter by date", widget=forms.RadioSelect(
        choices=[('Exact', False), ('Range', True)]))
    range_start = forms.DateField(label="Start", widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'textbox w-input'}))
    range_end = forms.DateField(label="End", widget=forms.DateInput(
        attrs={'type': 'date', 'class': 'textbox w-input'}))
    if date:
        range_start.required = True
        range_end.required = True
        # self.fields['range_end'].validators = [validateDates]


class BookingForm(forms.Form):
    class Meta:
        model = Booking
        fields = ("__all__")


class RatingForm(forms.Form):
    class Meta:
        model = Rating
        fields = ("rating")
