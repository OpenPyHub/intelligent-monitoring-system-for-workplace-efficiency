from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Affiliation, Workplace
from .forms import WorkplaceForm
from django.urls import reverse_lazy
from django.http import StreamingHttpResponse
from computer_vision.model import ChairMonitoring

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

def workplaceVideoFeed(request, pk): # function views
    workplace = Workplace.objects.get(pk=pk)

    workplace_id = pk
    video_path = workplace.media.path
    chair_coordinates = workplace.coordinates if workplace.coordinates else []

    monitoring = ChairMonitoring(workplace_id, video_path, chair_coordinates)
    video_stream = monitoring.monitor_chairs()

    return StreamingHttpResponse(video_stream, content_type='multipart/x-mixed-replace; boundary=frame')

class WorkplaceCreateView(CreateView): # class-based views
    model = Workplace
    template_name = 'workplace_new.html'
    form_class = WorkplaceForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class WorkplaceUpdateView(UpdateView): # class-based views
    model = Workplace
    template_name = 'workplace_edit.html'
    form_class = WorkplaceForm

class WorkplaceDeleteView(DeleteView): # class-based views
    model = Workplace
    template_name = 'workplace_delete.html'
    success_url = reverse_lazy('home')
