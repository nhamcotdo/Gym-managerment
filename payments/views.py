from django.shortcuts import render

from members.models import Member
from payments.models import Payments
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def history_payment(request, id):
    user = Member.objects.get(pk=id)
    payments = Payments.objects.filter(user=user)
    
    try:
        paginator = Paginator(payments, 100)
        page = request.GET.get('page', 1)
        payments = paginator.page(page)
    except PageNotAnInteger:
        payments = paginator.page(1)
    except EmptyPage:
        payments = paginator.page(paginator.num_pages)
    except Payments.DoesNotExist:
        payments = 'No Records'
    context = {
        'payments': payments,
    }
    return render(request, 'payments/history_payment.html', context)