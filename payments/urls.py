from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('history_payment/<int:id>/', login_required(views.history_payment), name='history_payment'),
]
