from django.urls import path

from . import views


urlpatterns = [
    path('timeline/<int:bio_id>/', views.timeline, name='biography-timeline'),
]
