from django.urls import path

from . import views

urlpatterns = [
    path('', (views.view_member), name='view_member'),
    path('view/', (views.view_member), name='view_member'),
    path('search/', (views.search_member), name='search_member'),
]