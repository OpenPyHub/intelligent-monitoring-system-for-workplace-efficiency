from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from .models import Affiliation, Workplace
from django.urls import reverse_lazy

# Create your views here.

def home(request): # function views
    return render(request, 'home.html')

class AboutUsPageView(TemplateView): # class-based views
    template_name = 'about-us.html'

class WorkplaceDetailView(DetailView): # class-based views
    model = Workplace
    template_name = 'workplace_detail.html'

class WorkplaceCreateView(CreateView): # class-based views
    model = Workplace
    template_name = 'workplace_new.html'
    fields = ['name', 'affiliation', 'body', 'media']

class WorkplaceUpdateView(UpdateView): # class-based views
    model = Workplace
    template_name = 'workplace_edit.html'
    fields = ['name', 'affiliation', 'body', 'media']

class WorkplaceDeleteView(DeleteView): # class-based views
    model = Workplace
    template_name = 'workplace_delete.html'
    success_url = reverse_lazy('home')
