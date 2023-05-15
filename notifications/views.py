from datetime import date
import logging
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render
from notifications.models import SearchForm
from payments.models import Member
logger = logging.getLogger(__name__)

# Create your views here.


def search(request):
    try:
        if request.method == 'GET':
            searchText = ''
            if request.GET.get('search'):
                searchText = request.GET.get('search')

            notifications = Member.objects.filter(
                first_name__contains=searchText).values('member_id', 'first_name', 'last_name', 'registration_date', 'registration_upto', 'subscription_period', 'subscription_type')
            results = []
            for notification in notifications:
                remaining_days = (
                    notification['registration_upto'] - date.today()).days
                if remaining_days > 7:
                    continue
                notification['status'] = f'Còn {remaining_days} ngày' if remaining_days > 0 else f'Đã hết hạn {-remaining_days} days'
                results.append(notification)
            search_form = SearchForm(request.GET)

            return render(request, 'notifications/index.html', {'results': results, 'search_form': search_form})
        else:
            return HttpResponseNotFound()
    except Exception as e:
        logger.error(e)
        return HttpResponseServerError()
