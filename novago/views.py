import json
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.conf import settings
import datetime
import pytz
import requests
from django.views.decorators.csrf import csrf_protect
import os
from django.core import serializers
# Create your views here.
from django.utils import timezone
from .models import *
from .forms import *
from authlib.integrations.django_client import OAuth
from urllib.parse import quote_plus, urlencode
from authlib.integrations.django_oauth2 import ResourceProtector
from . import validator
from django.urls import reverse
import stripe

# registers the remote application (novago)
# needs your variables set in env (i sent them, can again)
oauth = OAuth()

oauth.register(
    "novago",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    # this is the scope (so we can like deny access for driver/passenger or whatever right)
    # not sure though if should like not add any here then, only in the auth stuff?
    # should solve
    client_kwargs={
        "scope": "openid profile email",
    },
    # this is like the auth redirect url for some reason
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

DRIVER_PICS = ['driver1.jpg', 'driver2.jpg', 'driver3.jpg', 'driver4.jpg', 'driver5.jpg']


# should probably add csrf protect to these new functions?
# but not sure how that would work bc no forms really
# and they go to pages we don't have the html for really,,,

# after login redirects to home page


def callback(request):
    token = oauth.novago.authorize_access_token(request)
    request.session["user"] = token
    # makes a new account and passes id to create account or finds attached account
    if Account.objects.filter(sub=request.session.get("user")["userinfo"]["sub"]).count() != 0:
        request.session["user"]["user_id"] = Account.objects.filter(
            sub=request.session.get("user")["userinfo"]["sub"])[0].account_id
    else:
        a = Account(sub=request.session.get("user")["userinfo"]["sub"])
        a.save()
        request.session["user"]["user_id"] = a.account_id
        return redirect(request.build_absolute_uri(reverse('novago:create_account')))
    return redirect(request.build_absolute_uri(reverse('novago:index')))

# sends to auth0 login (callback)s


def login(request):
    return oauth.novago.authorize_redirect(
        request, request.build_absolute_uri(reverse("novago:callback"))
    )

# (hopefully logs out of all browsers ? will need to test)


def logout(request):
    request.session.clear()
    # clears session

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("novago:index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

# function to check if user is logged in
def check_scope(request):
    try:
        user_id = request.session.get("user").get("user_id")
    except:
        return False
    return user_id


# index view
# default shows all rides and no requests
@csrf_protect
def index(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        user_id = 22
    # only display upcoming trips with available seats
    user = Account.objects.get(pk=user_id)
    trips = [i if i.booked.count() <= i.passengers_amount and i.depart_date > datetime.date.today() and i.driver != Account.objects.get(pk=22) else '' for i in Trip.objects.all()]
    while trips.count('') != 0:
        trips.remove('')

    form = SearchForm(request.POST)

    data = serializers.serialize('python', trips)

    for d in data[:]:  # Make a copy of the original list to iterate over
        field = d['fields']
        if field['destination_address'] == '' or field['starting_address'] == '':
            data.remove(d)
        else:
            del field['date_published']
            del field['date_modified']
            del field['depart_time']
            del field['depart_date']

    data_list = [d['fields'] for d in data]

    context = {"user_id": user_id,
                'user': user,
               'triplist': trips,
               'form': form,
               'filters': FilterForm(request.POST),
               'json_trip_list': json.dumps(data_list),
               "session": request.session.get("user"),
               'google_api_key': settings.API_KEY,
               "pretty": json.dumps(request.session.get("user"), indent=4), }
    # only drivers see requests
    if Driver.objects.filter(account=user).count() != 0:
        trip_requests = [[i, Booking.objects.filter(trip=i)[0].account] if i.driver == Account.objects.get(pk=22) and Booking.objects.filter(trip=i).count() != 0 else '' for i in Trip.objects.all()]
        while trip_requests.count('') != 0:
            trip_requests.remove('')
        context['requestlist'] = trip_requests
    return render(request, 'main.html', context)


@ csrf_protect
def search(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    # currently filters by trip destination using filterLocation
    # request will eventually contain filter arguments which will dictate the search function
    destination_address = request.POST["where"]
    filtered_trips = Trip.objects.filter(
        destination_address=destination_address)
    
    # only display upcoming trips with available seats
    user = Account.objects.get(pk=user_id)
    trips = [i if i.booked.count() <= i.passengers_amount and i.depart_date > datetime.date.today() and i.driver != Account.objects.get(pk=22) else '' for i in filtered_trips]
    while trips.count('') != 0:
        trips.remove('')

    data = serializers.serialize('python', filtered_trips)
    for d in data[:]:  # Make a copy of the original list to iterate over
        field = d['fields']
        if field['destination_address'] == '' or field['starting_address'] == '':
            data.remove(d)
        else:
            del field['date_published']
            del field['date_modified']
            del field['depart_time']
            del field['depart_date']

    data_list = [d['fields'] for d in data]

    # k whatever were loading the page again
    context = {'user_id': user_id,
                'user': Account.objects.get(pk=user_id),
               'destination_address': destination_address,
               "session": request.session.get("user"),
               'triplist': filtered_trips,
               'json_trip_list': json.dumps(data_list),
               'form': SearchForm(request.POST),
               'google_api_key': settings.API_KEY}
    if Driver.objects.filter(account=user).count() != 0:
        trip_requests = [[i, Booking.objects.filter(trip=i)[0].account] if i.driver == Account.objects.get(pk=22) and Booking.objects.filter(trip=i).count() != 0 else '' for i in filtered_trips]
        while trip_requests.count('') != 0:
            trip_requests.remove('')
        context['requestlist'] = trip_requests
    return render(request, 'main.html', context)


def get_marker_data(request, destination_address):
    """AJAX call to get marker data"""
    if request.session.get("user"):
        user_id = request.session["user"]["user_id"]
    else:
        user_id = 1
    if request == 'GET':
        # get the search results from the database
        current_user = Account.objects.get(account_id=user_id)
        trip_list = Trip.objects.filter(
            destination_address=destination_address).exclude(driver=current_user)
        # return the results in a json format
        response_data = [{'address': trip.destination_address}
                         for trip in trip_list]
        return JsonResponse(response_data)


@ csrf_protect
def edit_profile(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    # if there's input, set user info
    user = Account.objects.get(pk=user_id)
    if request.POST.get("first_name") and request.POST.get("first_name") != "":
        user.first_name = request.POST.get("first_name")
    if request.POST.get("last_name") and request.POST.get("last_name") != "":
        user.last_name = request.POST.get("last_name")
    if request.POST.get("profile_description") and request.POST.get("profile_description") != "":
        user.profile_description = request.POST.get("profile_description")
    if request.POST.get("address") and request.POST.get("address") != "":
        user.address = request.POST.get("address")
    # can't write to heroku server in production for free so just choose a pic from our repo
    if request.FILES.get("profile_picture") and request.FILES.get("profile_picture") != "":
        user.profile_picture = request.FILES.get("profile_picture")
        hash_pic = user.profile_picture.__hash__()
        user.profile_picture = 'profile_pictures/' + DRIVER_PICS[hash_pic % 5]
    user.save()
    return redirect(request.build_absolute_uri(reverse('novago:profile')))


@ csrf_protect
def create_account(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    else:
        user=Account.objects.get(pk=user_id)
        pic = user.profile_picture
        context = {"user_id": user_id, "user": Account.objects.get(pk=user_id), 'pic': pic}
        return render(request, 'create-account.html', context)


@ csrf_protect
def reg_driver(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    if request.method == 'POST':
        if Driver.objects.filter(account=Account.objects.get(pk=user_id)).count() > 0:
            d = Driver.objects.get(account=Account.objects.get(pk=user_id))
        else:
            d = Driver(account=Account.objects.get(pk=user_id))
            d.save()
        if request.POST.get("master_number") and request.POST.get("master_number") != "":
            d.master_number = request.POST.get("master_number")
        if request.POST.get("license_expiry") and request.POST.get("license_expiry") != "":
            d.license_expiration_date = request.POST.get("license_expiry")
        if request.POST.get("license_plate") and request.POST.get("license_plate") != "":
            d.license_plate = request.POST.get("license_plate")
        if request.POST.get("driver_vin") and request.POST.get("driver_vin") != "":
            d.vehicle_information_number = request.POST.get("driver_vin")
        d.vehicle_picture = 'profile_pictures/car.jpg'
        d.save()
        return redirect(request.build_absolute_uri(reverse('novago:profile')))
    context = {'user_id': user_id,}
    if Driver.objects.filter(account=Account.objects.get(pk=user_id)).count() > 0:
        context['driver'] = Driver.objects.get(account=Account.objects.get(pk=user_id))
    return render(request, 'driver-reg.html', context)

def upload(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    user = Account.objects.get(pk=user_id)
    form = AccountForm(instance=user)
    if request.method == "POST":
            form = AccountForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
            return redirect('novago:profile', user_id)
    else:
        form = AccountForm(instance=user)
    return render(request, 'upload.html', context= {'form':form })



@ csrf_protect
def profile(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    user = Account.objects.get(pk=user_id)
    ratings = []
    for r in Rating.objects.all():
        if r.booking.trip.driver == user and r.rating != None:
            ratings.append(r)
    trips = [i if i.depart_date > datetime.date.today() else '' for i in Trip.objects.filter(driver=user)]
    while trips.count('') != 0:
        trips.remove('')
    stars = range(int(user.rating))
    context = {'user': user,
               'user_id': user_id,
               'session': request.session.get("user"),
               'review_list': ratings,
               'trip_list': trips, 
               'stars': stars,}
    if user.rating - int(user.rating) >= 0.5:
        context["half"] = True
    return render(request, 'profile.html', context)

# show profile of another user
def user_profile(request, driver):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    driver = Account.objects.get(pk=driver)
    ratings = []
    for r in Rating.objects.all():
        if r.booking.trip.driver == driver and r.rating != None:
            ratings.append(r)
    trips = [i if i.depart_date > datetime.date.today() else '' for i in Trip.objects.filter(driver=driver)]
    while trips.count('') != 0:
        trips.remove('')
    stars = range(int(driver.rating))
    context = {'user': driver,
               'user_id': user_id,
               'session': request.session.get("user"),
               'review_list': ratings,
               'trip_list': trips, 
               'stars': stars}
    if driver.rating - int(driver.rating) >= 0.5:
        context["half"] = True
    return render(request, 'profile.html', context)


@ csrf_protect
def new_trip(request):
    """send form to url path /new-trip"""
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    # render form
    form = TripForm()
    user = Account.objects.get(pk=user_id)
    destination_address = ' empty '

    # if the request is post
    if request.method == 'POST':
        # generate the trip from the info given by request
        form = TripForm(request.POST)

        # if the form is validated (the user entered the info correctly)
        if form.is_valid():
            # save the trip
            my_trip = form.save()
            # add myself to the trip for the manytomany relationship
            destination_address = my_trip.destination_address
            my_trip.driver = user
            b = Booking(trip=my_trip, account=user)
            b.save()
            my_trip.booked.add(user)
            my_trip.save()
            print(my_trip)
            return redirect(request.build_absolute_uri(reverse('novago:index')))
    context = {'form': form,
               'destination_address': destination_address,
               'user_id': user_id,
               'user': user,
               'google_api_key': settings.API_KEY,
               'session': request.session.get("user")}
    if Driver.objects.filter(account=user).count() > 0:
        print(Driver.objects.filter(account=user).count())
        context["driver"] = True
    return render(request, 'new-trip.html', context)


# request a trip
@ csrf_protect
def new_request(request):
    """send form to url path /new-request"""
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    user = Account.objects.get(pk=user_id)
    # render form
    form = TripForm()

    destination_address = ' empty '

    # if the request is post
    if request.method == 'POST':
        # generate the trip from the info given by request
        form = TripForm(request.POST)

        # if the form is validated (the user entered the info correctly)
        if form.is_valid():
            # save the trip
            my_trip = form.save()
            # add myself to the trip for the manytomany relationship
            destination_address = my_trip.destination_address
            my_trip.driver = Account.objects.get(pk=22)
            b = Booking(trip=my_trip, account=user)
            b.save()
            my_trip.booked.add(user)
            my_trip.save()
            print(my_trip)
            return redirect(request.build_absolute_uri(reverse('novago:index')))
    context = {'form': form,
               'destination_address': destination_address,
               'user_id': user_id,
               'user': user,
               'google_api_key': settings.API_KEY,
               'session': request.session.get("user")}
    # a driver chose to make a request
    if Driver.objects.filter(account=user).count() > 0:
        context["driver"] = False
    return render(request, 'new-trip.html', context)


# load past future and personal trips
@ csrf_protect
def yourTrips(request, message = 0):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    account_driver_or_passenger = Booking.objects.filter(account=user_id)
    upcoming_trips = []
    past_trips = []
    your_trips = []
    rated_trips = []
    # set time zone to UTC just for comparison
    utc = pytz.UTC

    # get the trip associated with the account in m2m table
    # ! need to check logic here, what are we allowing the user to edit?

    for row in account_driver_or_passenger:
        # set time zone to UTC just for comparison
        # get time from trip (requires concatenation, may look into changing this in model)
        date_of_trip = row.trip.depart_date
        time_of_trip = row.trip.depart_time
        datetime_of_trip = utc.localize(
            datetime.datetime.combine(date_of_trip, time_of_trip))
        if row.trip.driver == row.account:
            your_trips.append(row.trip)
        elif datetime_of_trip > timezone.now():
            upcoming_trips.append(row.trip)
        else:
            past_trips.append(row.trip)
            if len(Rating.objects.filter(booking=row)) > 0:
                rated_trips.append(row.trip)

    context = {'your_trips': your_trips,
               'upcoming_trips': upcoming_trips,
               'past_trips': past_trips,
               'rated_trips': rated_trips,
               'user_id': user_id, 
               'user': Account.objects.get(pk=user_id),
               'session': request.session.get("user")}
    if message == 1:
        context['message'] = "Too many passengers on this trip already, sorry."
    elif message == 2:
        context['message'] = "You're already a passenger on this trip!"
    elif message == 3:
        context['message'] = "Sorry, you can only rate trips when you're a passenger."
    return render(request, 'your-trips.html', context)


# add a rating and review to a users profile
@ csrf_protect
def rate(request, trip_id):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    if request.POST:
        rating = float(request.POST.get('rating'))
        trip = Trip.objects.get(pk=trip_id)
        user = Account.objects.get(pk=user_id)
        if Booking.objects.filter(trip=trip, account=user).count() > 0:
            bking = Booking.objects.get(trip=trip, account=user)
            if rating > 5.0 or rating < 0.0:
                form = RatingForm(request.POST)
                context = {'form': form, 'trip': trip_id, 'message': 'Please enter a value between 0 and 5.'}
                return render(request, 'rate.html', context)
            driver = trip.driver
            rr = Rating(booking=bking, rating=rating, description=request.POST.get('description'))
            rr.save()
            ratings = []
            for r in Rating.objects.all():
                if r.booking.trip.driver == driver:
                    ratings.append(r)
            rSum = 0
            for r in ratings:
                if r.rating != None:
                    rSum += float(r.rating)
            rRating = rSum / len(ratings)
            driver.rating = rRating
            driver.save()
            return redirect(request.build_absolute_uri(reverse('novago:your-trips')))
        else:
            return redirect(request.build_absolute_uri(reverse('novago:failed', args=(3,))))
    else:
        form = RatingForm(request.POST)
        context = {'form': form, 'trip': trip_id}
        return render(request, 'rate.html', context)


@ csrf_protect
def modify_trip(request, trip_id):
    """display form to modify trip"""
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    # get the trip form
    trip = Trip.objects.get(pk=trip_id)
    form = TripForm(instance=trip)
    passenger_list = [passenger for passenger in trip.booked.all()]
    passenger_list.sort(key=lambda passenger: passenger.first_name)

    # remove driver from passenger list
    passenger_list.remove(Account.objects.get(pk=user_id))

    if request.method == 'POST':
        # generate the trip from the info given by request
        form = TripForm(request.POST, instance=trip)

        if form.is_valid():
            # save the trip
            form.save()

            # my_trip = form.save()
            # # add myself to the trip for the manytomany relationship
            # my_trip.booked.add(Account.objects.get(pk=user_id))
            return redirect(request.build_absolute_uri(reverse('novago:your-trips')))

    context = {'form': form,
               'passenger_list': passenger_list,
               'trip_id': trip_id,
               'user_id': user_id,
               'user': Account.objects.get(pk=user_id),
               'google_api_key': settings.API_KEY,
               'user_id': user_id, }
    return render(request, 'modify.html', context)


@ csrf_protect
def kick_passenger(request, trip_id, passenger_id):
    """from modify view, kick a passenger from a trip"""
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    trip = Trip.objects.get(pk=trip_id)
    passenger = Account.objects.get(pk=passenger_id)
    trip.booked.remove(passenger)

    next = request.POST.get('next', '/')

    return modify_trip(request, user_id, trip_id)


@ csrf_protect
def kick_yourself(request, trip_id):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    trip = Trip.objects.get(pk=trip_id)
    passenger = Account.objects.get(pk=user_id)
    trip.booked.remove(passenger)
    next = request.POST.get('next', '/')
    return yourTrips(request)


def cancel_trip(request, trip_id):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    try:
        trip = Trip.objects.get(pk=trip_id)
        trip.delete()
        next = request.POST.get('next', '/')
    except:
        next = request.POST.get('next', '/')
    return yourTrips(request)


@ csrf_protect
def route(request):
    # render form
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    form = TripForm()

    # if the request is post
    if request.method == 'POST':
        # generate the trip from the info given by request
        form = TripForm(request.POST)

        # if the form is validated (the user entered the info correctly)
        if form.is_valid():
            # save the trip
            my_trip = form.save()

            # add myself to the trip for the manytomany relationship
            my_trip.booked.add(Account.objects.get(pk=user_id))

    context = {'form': form, 'user_id': user_id,
               'google_api_key': settings.API_KEY}

    return render(request, 'route.html', context)


@ csrf_protect
def book_trip(request, destination_address):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    print("destination_address", destination_address)

    bookings = Booking.objects.all()

    filtered_trips = Trip.objects.filter(
        destination_address=destination_address)

    data = serializers.serialize('python', filtered_trips)
    for d in data[:]:  # Make a copy of the original list to iterate over
        field = d['fields']
        if field['destination_address'] == '' or field['starting_address'] == '':
            data.remove(d)
        else:
            del field['date_published']
            del field['date_modified']
            del field['depart_time']
            del field['depart_date']

    data_list = [d['fields'] for d in data]

    context = {'bookinglist': bookings,
               'destination_address': destination_address,
               'triplist': filtered_trips,
               'json_trip_list': json.dumps(data_list),
               'user_id': user_id,
               'google_api_key': settings.API_KEY, }

    return render(request, 'book-trip.html', context)


@csrf_protect
def stripe_config(request):
    if request.method == 'GET':
        print(settings.STRIPE_PUBLISHABLE_KEY)
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        print(JsonResponse(stripe_config, safe=False))


@csrf_protect
def create_checkout_session(request):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    stripe_config(request)
    domain_url = 'http://127.0.0.1:8000/'
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + 'cancelled/',
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'name': 'T-shirt',
                    'quantity': 1,
                    'currency': 'usd',
                    'amount': '2000',
                }
            ]
        )
        print(JsonResponse({'sessionId': checkout_session['id']}))
    except Exception as e:
        print(JsonResponse({'error': str(e)}))
    return redirect(request.build_absolute_uri(reverse('novago:profile')))


@ csrf_protect
def see_info(request, trip):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    context = {'trip': Trip.objects.get(pk=trip),
               'session': request.session.get("user"),
               'user': Account.objects.get(pk=user_id)}
    return render(request, 'book-trip.html', context)


# book a trip
@ csrf_protect
def book(request, trip_id):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    user = Account.objects.get(pk=user_id)
    trip = Trip.objects.get(pk=trip_id)
    if trip.booked.count() >= trip.passengers_amount:
        return redirect(request.build_absolute_uri(reverse('novago:failed', args=(1,))))
    else:
        if Booking.objects.filter(trip=trip).filter(account=user).count() == 0:
            b = Booking(trip=trip, account=user)
            b.save()
            trip.booked.add(user)
            price = trip.price
            driver = trip.driver.first_name
            context = {'price': price, 'driver': driver}
            return redirect(request.build_absolute_uri(reverse('novago:your-trips')))
        else:
            return redirect(request.build_absolute_uri(reverse('novago:failed', args=(2,))))


# accept a trip request
@ csrf_protect
def take(request, trip_id):
    # call check scope
    # if not logged in, send to login, otherwise continue
    user_id = check_scope(request)
    if not user_id:
        return redirect(request.build_absolute_uri(reverse('novago:login')))
    user = Account.objects.get(pk=user_id)
    trip = Trip.objects.get(pk=trip_id)
    owner = Booking.objects.get(trip=trip).account
    # has to make a new trip with this user as a driver
    newtrip = Trip(driver=user, destination_address=trip.destination_address, starting_address=trip.starting_address, depart_date=trip.depart_date, depart_time=trip.depart_time, price=trip.price, stops=trip.stops)
    if trip.passengers_amount == 0:
        newtrip.passengers_amount = 1
    newtrip.save()
    b = Booking(account=user, trip=newtrip)
    b.save()
    if owner != user:
        b = Booking(account=owner, trip=newtrip)
        b.save()
    newtrip.booked.add(user)
    newtrip.booked.add(owner)
    newtrip.save()
    trip.delete()
    return redirect(request.build_absolute_uri(reverse('novago:your-trips')))

