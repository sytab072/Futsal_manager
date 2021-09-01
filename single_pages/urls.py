from django.urls import path
from . import views

urlpatterns = [
    path('about_site/', views.about_site),
    path('',views.landing),
]