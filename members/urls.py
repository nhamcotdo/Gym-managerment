from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    
    path('', login_required(views.members), name='members'),
    path('add/', login_required(views.add_member), name='add_member'),
    path('view/', login_required(views.view_member), name='view_member'),
    path('search/', (views.search_member), name='search_member'),
    path('update/<int:id>/', login_required(views.update_member), name='update_member'),
]