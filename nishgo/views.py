from django.shortcuts import redirect
from novago import urls


def redirect_view(request):
    # user_id change to user who is logged in
    # !for OAuth login
    response = redirect('novago:index')
    return response
