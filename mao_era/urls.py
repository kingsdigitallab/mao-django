from django.urls import path

from . import views


urlpatterns = [
    path('pdf/biography/<int:bio_id>/', views.biography_pdf,
         name='biography-pdf'),
    path('pdf/source/<int:source_id>/', views.source_pdf, name='source-pdf'),
    path('timeline/', views.full_timeline, name='full-timeline'),
    path('timeline/<int:bio_id>/', views.bio_timeline,
         name='biography-timeline'),
]
