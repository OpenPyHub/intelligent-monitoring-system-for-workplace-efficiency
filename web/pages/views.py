from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Affiliation, Workplace
from .forms import WorkplaceForm
from django.urls import reverse_lazy

# Create your views here.

def home(request): # function views
    return render(request, 'home.html')

class AboutUsPageView(TemplateView): # class-based views
    template_name = 'about-us.html'

class WorkplaceListView(ListView): # class-based views
    model = Workplace
    template_name = 'workplaces.html'

class WorkplaceDetailView(DetailView): # class-based views
    model = Workplace
    template_name = 'workplace_detail.html'

class WorkplaceCreateView(CreateView): # class-based views
    model = Workplace
    template_name = 'workplace_new.html'
    form_class = WorkplaceForm

class WorkplaceUpdateView(UpdateView): # class-based views
    model = Workplace
    template_name = 'workplace_edit.html'
    form_class = WorkplaceForm

class WorkplaceDeleteView(DeleteView): # class-based views
    model = Workplace
    template_name = 'workplace_delete.html'
    success_url = reverse_lazy('home')
