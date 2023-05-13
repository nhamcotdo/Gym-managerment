from django.shortcuts import render
from payments.models import Payments
from django.http import JsonResponse
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import datetime

def index(request):
    return render(request, 'dashboards/index.html')

def get_revenue(request):
    if request.method == 'GET':
        if request.GET.get('year'):
            year = request.GET.get('year')
            today = datetime.date.today()
            payments = Payments.objects.filter(payment_date__year=year).values('payment_date', 'payment_amount')
            total_amount_select = payments.aggregate(total=Sum('payment_amount'))['total']

            payments_lastyear = Payments.objects.filter(payment_date__year=int(today.year)-1).values('payment_date', 'payment_amount')
            total_amount_lastyear = payments_lastyear.aggregate(total=Sum('payment_amount'))['total']
            payments_cur = Payments.objects.filter(payment_date__year=today.year).values('payment_date', 'payment_amount')
            total_amount = payments_cur.aggregate(total=Sum('payment_amount'))['total']
            
            current_month = today.month
            
            amounts_by_month = {month: 0 for month in range(1, 13)}
            
            for payment in payments:
                payment_date = payment['payment_date']
                month = payment_date.month
                amount = payment['payment_amount']
                amounts_by_month[month] += amount
            
            current_month_amount = amounts_by_month.get(current_month, 0)
            last_month_payments = Payments.objects.filter(payment_date__year=today.year-1, payment_date__month=current_month).values('payment_amount')
            last_month_amount = last_month_payments.aggregate(total=Sum('payment_amount'))['total']
            
            response = {
                'total_amount': total_amount or '0',
                'total_amount_lastyear': total_amount_lastyear or '1',
                'amounts_by_month': amounts_by_month,
                'current_month_amount': current_month_amount or '0',
                'last_month_amount': last_month_amount or '0',
                'total_amount_select': total_amount_select or '0',
            }
            
            return JsonResponse(response, encoder=DjangoJSONEncoder)

def get_years(request):
    if request.method == 'GET':
        payments = Payments.objects.values('payment_date')
        list_years = payments.values_list('payment_date__year', flat=True).distinct()
        response = {
            'list_years': list(list_years),
            'current_year': datetime.date.today().year
        }
        
    return JsonResponse(response, encoder=DjangoJSONEncoder)