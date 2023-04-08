from django.contrib import admin
from .models import Account, Trip, Booking

# Register your models here.
admin.site.register(Account)
admin.site.register(Trip)
admin.site.register(Booking)
