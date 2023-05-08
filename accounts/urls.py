from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', (views.homepage_after_login), name="homepage_after_login"),
]