from django.urls import path
from . import views
from .views import AboutUsPageView, WorkplaceListView, WorkplaceDetailView, WorkplaceCreateView, WorkplaceUpdateView, WorkplaceDeleteView, workplaceVideoFeed

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', AboutUsPageView.as_view(), name='about-us'),
    path('workplaces/', WorkplaceListView.as_view(), name='workplaces'),
    path('workplaces/<int:pk>/', WorkplaceDetailView.as_view(), name='workplace_detail'),
    path('workplaces/<int:pk>/video_feed/', workplaceVideoFeed, name='workplace_video_feed'),
    path('workplaces/new/', WorkplaceCreateView.as_view(), name='workplace_new'),
    path('workplaces/<int:pk>/edit/', WorkplaceUpdateView.as_view(), name='workplace_edit'),
    path('workplaces/<int:pk>/delete/', WorkplaceDeleteView.as_view(), name='workplace_delete'),
]
