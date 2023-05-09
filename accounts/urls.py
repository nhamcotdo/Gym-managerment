from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.homepage_after_login), name="homepage_after_login"),
    path('login/', views.loginCustom, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-change/', login_required(views.password_change, login_url='login'), name='changePassword'),
]