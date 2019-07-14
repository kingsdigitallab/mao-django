from django.urls import path

from . import views


urlpatterns = [
    path('timeline/', views.full_timeline, name='full-timeline'),
    path('timeline/<int:bio_id>/', views.bio_timeline,
         name='biography-timeline'),
]
