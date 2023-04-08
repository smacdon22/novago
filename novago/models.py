from django.db import models
from django import utils
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Account(models.Model):
    """Account class, holds profile data"""
    account_id = models.AutoField(primary_key=True)
    first_name = models.CharField(
        max_length=255,
        default='John'
    )
    last_name = models.CharField(
        max_length=255,
        default='Doe'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='driver1.jpg'

    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=2.5
    )
    profile_description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    # auth0 user code
    sub = models.CharField(max_length=250, default='')

    def __str__(self):
        """to_string overide"""
        return f"{self.account_id} - {self.first_name} - {self.last_name}"


class Driver(models.Model):
    """driver class, holds vehicle and license information"""
    # driver info
    account = models.OneToOneField(
        Account,
        default=1,
        on_delete=models.CASCADE,
        related_name='account_of_driver'
    )
    master_number = models.CharField(max_length=250, default='')
    license_expiration_date = models.DateField(
        auto_now_add=False,
        default=utils.timezone.now
    )
    license_plate = models.CharField(max_length=25, default="AAA 123")
    vehicle_information_number = models.CharField(max_length=250, default='')
    vehicle_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='driver1.jpg'
    )



class Trip(models.Model):
    """Trip class, holds trip data and a driver account foreign key"""
    trip_id = models.AutoField(primary_key=True)
    destination_address = models.CharField(max_length=255)
    starting_address = models.CharField(max_length=255, default='', blank=True)
    depart_date = models.DateField(
        auto_now_add=False,
        default=utils.timezone.now
    )
    depart_time = models.TimeField(
        auto_now=False,
        auto_now_add=False,
        default=utils.timezone.now
    )
    price = models.IntegerField(default=10)
    date_published = models.DateTimeField(
        auto_now_add=True,
        verbose_name='time stamp of trip creation'
    )
    date_modified = models.DateTimeField(auto_now=True)
    stops = models.BooleanField(default=0)
    driver = models.ForeignKey(
        Account,
        default=1,
        on_delete=models.CASCADE,
        related_name='driver_of_trip'
    )
    passengers_amount = models.IntegerField(default=0)
    booked = models.ManyToManyField(
        Account,
        through='Booking',
        through_fields=('trip', 'account')
    )

    def __str__(self):
        return f"ID:{self.trip_id} - Driver: {self.driver.first_name} - Destination: {self.destination_address}"


class Booking(models.Model):
    """Booking Connecting Table"""

    # could possibly be on_delete= models.SET_NULL
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='account_of_passenger'
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='trip_associated_to_passenger'
    )

    class Meta:
        """ensures that a combination of account and trip values is unique"""
        unique_together = ('account', 'trip')

    def __str__(self):
        """to_string overide"""
        if self.trip.driver == self.account:
            concatenated = "" + \
                f"{self.account} is the driver for the trip: {self.trip}"
        else:
            concatenated = "" + \
                f"{self.account} is a passenger in trip: {self.trip}"

        return concatenated


class Rating(models.Model):
    """Rating table"""
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking'
    )
    rating = models.DecimalField(default=None, decimal_places=2, max_digits=3, blank=True,)
    description = models.CharField(max_length=255, blank=True)
