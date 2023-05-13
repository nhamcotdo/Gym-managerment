from django.urls import path, include
from django.contrib.auth.decorators import login_required


from . import views

urlpatterns = [
    path('',  login_required(views.index, login_url='login'), name='index'),
    path('get_revenue',  login_required(views.get_revenue, login_url='login'), name='get_revenue'),
    path('get_years',  login_required(views.get_years, login_url='login'), name='get_years'),
]