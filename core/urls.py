from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('about-us/', views.about, name='about'),
    path('contact-us/', views.contact, name='contact'),
    path('programs/', views.programs, name='programs'),
    path('blog/', views.blog, name='blog'),
]