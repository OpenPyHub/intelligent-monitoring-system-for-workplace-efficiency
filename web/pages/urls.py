from django.urls import path
from . import views
from .views import AboutUsPageView, WorkplaceDetailView, WorkplaceCreateView, WorkplaceUpdateView, WorkplaceDeleteView

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', AboutUsPageView.as_view(), name='about-us'),
    path('workplace/<int:pk>/', WorkplaceDetailView.as_view(), name='workplace_detail'),
    path('workplace/new/', WorkplaceCreateView.as_view(), name='workplace_new'),
    path('workplace/<int:pk>/edit/', WorkplaceUpdateView.as_view(), name='workplace_edit'),
    path('workplace/<int:pk>/delete/', WorkplaceDeleteView.as_view(), name='workplace_delete'),
]
