from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from .models import AddMemberForm, Member, SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from payments.models import Payments
from django.db.models.signals import post_save
import dateutil.parser as parser
from notifications.config import my_handler
import datetime, csv
import dateutil.relativedelta as delta



# Export user information.
def export_all(user_obj):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['First name', 'Last name', 'Mobile', 'Admission Date', 'Subscription Type', 'Batch'])
    members = user_obj.values_list('first_name', 'last_name', 'mobile_number', 'admitted_on', 'subscription_type', 'batch')
    for user in members:
        first_name = user[0]
        last_name = user[1]
        writer.writerow(user)

    response['Content-Disposition'] = 'attachment; filename="' + first_name + ' ' + last_name + '.csv"'
    return response


def members(request):
    form = AddMemberForm()
    context = {
        'form': form,
        #'subs_end_today_count': get_notification_count(),
    }
    return render(request, 'members/add_member.html', context)


def model_save(model):
    post_save.disconnect(my_handler, sender=Member)
    model.save()
    post_save.connect(my_handler, sender=Member)

def check_status(request, object):
    object.stop = 1 if request.POST.get('stop') == '1' else 0
    return object

def view_member(request):
    view_all = Member.objects.filter(stop=0).order_by('first_name')
    paginator = Paginator(view_all, 100)
    try:
        page = request.GET.get('page', 1)
        view_all = paginator.page(page)
    except PageNotAnInteger:
        view_all = paginator.page(1)
    except EmptyPage:
        view_all = paginator.page(paginator.num_pages)
    search_form = SearchForm()
    context = {
        'all': view_all,
        'search_form': search_form,
        #'subs_end_today_count': get_notification_count(),
    }
    return render(request, 'members/view_member.html', context)
    # return render(request, 'members/view_member.html')

def search_member(request):
    if request.method == 'POST':
        # search_form = SearchForm(request.POST)
        # first_name = request.POST.get('search')
        # check = Member.objects.filter(first_name__contains=first_name)
        # check = serializers.serialize('json', check)
        # context = {}
        # context['search'] = check
        if 'clear' in request.POST:
            return redirect('view_member')
        search_form = SearchForm(request.POST)
        result = 0
        if search_form.is_valid():
            first_name = request.POST.get('search')
            result = Member.objects.filter(first_name__contains=first_name)
            print(result)

        view_all = Member.objects.all()

        context = {
            'all': view_all,
            'search_form': search_form,
            'result': result,
            #'subs_end_today_count': get_notification_count(),
        }
        return render(request, 'members/view_member.html', context)
    else:
        search_form = SearchForm()
    return render(request, 'members/view_member.html', {'search_form': search_form})

def add_member(request):
    view_all = Member.objects.all()
    success = 0
    member = None
    if request.method == 'POST':
        form = AddMemberForm(request.POST, request.FILES)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.first_name = request.POST.get('first_name').capitalize()
            temp.last_name = request.POST.get('last_name').capitalize()
            temp.registration_upto = parser.parse(request.POST.get('registration_date')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
            if request.POST.get('fee_status') == 'pending':
                temp.notification = 1

            model_save(temp)
            success = 'Successfully Added Member'

            # Add payments if payment is 'paid'
            if temp.fee_status == 'paid':
                payments = Payments(
                                    user=temp,
                                    payment_date=temp.registration_date,
                                    payment_period=temp.subscription_period,
                                    payment_amount=temp.amount)
                payments.save()

            form = AddMemberForm()
            member = Member.objects.last()

        context = {
            'add_success': success,
            'form': form,
            'member': member,
            #'subs_end_today_count': get_notification_count(),
        }
        return render(request, 'members/add_member.html', context)
    else:
        form = AddMemberForm()
        context = {
            'form': form,
            #'subs_end_today_count': get_notification_count(),
        }
    return render(request, 'members/add_member.html', context)
