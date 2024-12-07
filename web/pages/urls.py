from django.urls import path
from . import views
from .views import AboutUsPageView

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', AboutUsPageView.as_view(), name='about-us'),
]
