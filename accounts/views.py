from django.shortcuts import render

# Create your views here.
def homepage_after_login(request):
    return render(request, 'base.html')