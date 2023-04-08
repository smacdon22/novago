from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *

app_name = 'novago'

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('create-account/', create_account, name='create_account'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('driver/', reg_driver, name='reg_driver'),
    path('search/', search, name='search'),
    path('callback/', callback, name='callback'),
    path('new-trip/', new_trip, name='new-trip'),
    path('new-request/', new_request, name='new-request'),
    path('your-trips/modify_trip/<int:trip_id>',
         modify_trip, name='modify_trip'),
    path('your-trips/cancel_trip/<int:trip_id>',
         cancel_trip, name='cancel_trip'),
    path('your-trips/modify_trip/kick_passenger/<int:trip_id>/<int:passenger_id>',
         kick_passenger, name='kick_passenger'),
    path('your-trips/kick-yourself/<int:trip_id>',
         kick_yourself, name='kick-yourself'),
    path('your-trips/', yourTrips, name='your-trips'),
    path('your-trips/<int:trip_id>-booked', book, name='book'),
    path('your-trips/<int:trip_id>-accepted', take, name='take'),
    path('your-trips/booking-failed/<int:message>', yourTrips, name='failed'),
    path('<destination_address>/get_marker_data/',
         get_marker_data, name='get_marker_data'),
    path('profile/', profile, name='profile'),
    path('profile/<int:driver>', user_profile, name='user-profile'),
    path('rate/<int:trip_id>', rate, name='rate'),
    path('config/', stripe_config, name='config'),  # new
    path('create-checkout-session/', create_checkout_session,
         name='create_checkout_session'),  # new
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
