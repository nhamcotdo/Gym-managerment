from django.urls import path, include
from django.contrib.auth.decorators import login_required


from . import views

urlpatterns = [
    path('',  login_required(views.index, login_url='login'), name='index'),
]