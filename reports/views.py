from django.shortcuts import render, redirect
from django.http import HttpResponse
from members.models import Member
import csv
import datetime
from .models import GenerateReportForm
from django.db.models import Q
from notifications.config import get_notification_count

# Create your views here.
def export_all(user_obj):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['First name', 'Last name', 'DOB', 'Mobile', 'Subscription Type'])
    members = user_obj.values_list('first_name', 'last_name', 'dob', 'mobile_number', 'subscription_type')
    for user in members:
        writer.writerow(user)

    return response

def reports(request):
    if request.method == 'POST':
        form = GenerateReportForm(request.POST)
        if form.is_valid():
            if request.POST.get('month') and request.POST.get('year'):
                query = Q(
                    registration_date__month=request.POST.get('month'),
                    registration_date__year=request.POST.get('year'),
                )
            else:
                query = Q()
            users = Member.objects.filter(query)
            if 'export' in request.POST:
                return export_all(users)
            context = {
                'users': users,
                'form': form,
                'subs_end_today_count': get_notification_count(),
            }
            return render(request, 'reports/reports.html', context)
    else:
        form = GenerateReportForm()
    return render(request, 'reports/reports.html', {'form': form, 'subs_end_today_count': get_notification_count()})
