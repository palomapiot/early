from django.shortcuts import render
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

# Create your views here.

# TODO: esto no esta haciendo nada
def index(request):
    """View function for home page of site."""
    # Render the HTML template index.html with the data in the context variable
    if request.user.is_authenticated:
        return render(request, 'index.html')
    else:
        return render(request, 'registration/login.html')
