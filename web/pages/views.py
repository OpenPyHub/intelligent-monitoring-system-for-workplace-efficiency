from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

def home(request): # function views
    return render(request, 'home.html')

class AboutUsPageView(TemplateView): # class-based views
    template_name = 'about-us.html'
