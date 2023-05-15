from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from .models import AddMemberForm, Member, SearchForm, UpdateMemberGymForm, UpdateMemberInfoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from payments.models import Payments
from django.db.models.signals import post_save
import dateutil.parser as parser
from notifications.config import my_handler
import datetime, csv
import dateutil.relativedelta as delta
from django.contrib import messages

# Export user information.
def export_all(user_obj):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['First name', 'Last name', 'Mobile', 'Admission Date', 'Subscription Type'])
    members = user_obj.values_list('first_name', 'last_name', 'mobile_number', 'subscription_type')
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
    view_all1 = Member.objects.filter(stop=1).order_by('first_name')
    paginator = Paginator(view_all, 100)
    paginator1 = Paginator(view_all1, 100)
    try:
        page = request.GET.get('page', 1)
        view_all = paginator.page(page)
        view_all1 = paginator1.page(page)
    except PageNotAnInteger:
        view_all = paginator.page(1)
        view_all1 = paginator1.page(1)
    except EmptyPage:
        view_all = paginator.page(paginator.num_pages)
        view_all1 = paginator1.page(paginator1.num_pages)
    search_form = SearchForm()
    context = {
        'all': view_all,
        'all1': view_all1,
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
                                    payment_date=datetime.date.today(),
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

def update_member(request, id):
    if request.method == 'POST' and request.POST.get('export'):
        return export_all(Member.objects.filter(pk=id))
    if request.method == 'POST' and request.POST.get('no'):
        return redirect('/')
    #return render(request, 'members/update_member.html')
    if request.method == 'POST' and request.POST.get('gym_membership'):
            gym_form = UpdateMemberGymForm(request.POST)
            if gym_form.is_valid():
                object = Member.objects.get(pk=id)
                amount = request.POST.get('amount')
                day = (parser.parse(request.POST.get('registration_upto')) - delta.relativedelta(months=int(request.POST.get('subscription_period')))).day
                last_day = parser.parse(str(object.registration_upto)).day

                month = parser.parse(request.POST.get('registration_upto')).month
                last_month = parser.parse(str(object.registration_upto)).month
                # if status is stopped then do not update anything
                if object.stop == 1 and not request.POST.get('stop') == '0' and request.POST.get('gym_membership'):
                    messages.error(request, 'Bạn phải kích hoạt tài khoản trước chỉnh sửa')
                    return redirect('update_member', id=object.pk)
                # check if user has modified only the date
                elif (datetime.datetime.strptime(str(object.registration_date), "%Y-%m-%d") != datetime.datetime.strptime(request.POST.get('registration_date'), "%Y-%m-%d")):
                        object.registration_date =  parser.parse(request.POST.get('registration_date'))
                        object.registration_upto =  parser.parse(request.POST.get('registration_date')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                        object.fee_status = request.POST.get('fee_status')
                        object = check_status(request, object)
                        model_save(object)
                # if amount and period are changed
                elif (object.amount != amount) and (object.subscription_period != request.POST.get('subscription_period')):
                    object.subscription_type =  request.POST.get('subscription_type')
                    object.subscription_period =  request.POST.get('subscription_period')
                    object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                    object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    object.fee_status = request.POST.get('fee_status')
                    object.amount =  request.POST.get('amount')
                    object = check_status(request, object)
                    model_save(object)
                # if only subscription_period is Changed
                elif (object.subscription_period != request.POST.get('subscription_period')):
                    object.subscription_period =  request.POST.get('subscription_period')
                    object = check_status(request, object)
                    model_save(object)
                # if amount and type are changed
                elif (object.amount != amount) and (object.subscription_type != request.POST.get('subscription_type')):
                    object.subscription_type =  request.POST.get('subscription_type')
                    object.subscription_period =  request.POST.get('subscription_period')
                    object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                    object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    object.fee_status = request.POST.get('fee_status')
                    object.amount =  request.POST.get('amount')
                    object = check_status(request, object)
                    model_save(object)
                # if amount ad fee status are changed
                elif (object.amount != amount) and ((request.POST.get('fee_status') == 'paid') or (request.POST.get('fee_status') == 'pending')):
                        object.amount = amount
                        object.fee_status = request.POST.get('fee_status')
                        object = check_status(request, object)
                        model_save(object)
                # if only amount is channged
                elif (object.amount != amount):
                    object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                    object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    object.fee_status = request.POST.get('fee_status')
                    object.amount =  request.POST.get('amount')
                    if request.POST.get('fee_status') == 'pending':
                        object.notification =  1
                    elif request.POST.get('fee_status') == 'paid':
                        object.notification = 2
                    object = check_status(request, object)
                    model_save(object)
                # nothing is changed
                else:
                    print('195')
                    if not request.POST.get('stop') == '0':
                        object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                        object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                        object.amount =  request.POST.get('amount')
                        if request.POST.get('fee_status') == 'pending':
                            object.notification =  1
                        elif request.POST.get('fee_status') == 'paid':
                            object.notification = 2
                    object.fee_status = request.POST.get('fee_status')
                    object = check_status(request, object)
                    model_save(object)

                # Add payments if payment is 'paid'
                if object.fee_status == 'paid':
                    check = Payments.objects.filter(
                        payment_date=object.registration_date,
                        user__pk=object.pk).count()
                    if check == 0:
                        payments = Payments(
                                            user=object,
                                            payment_date=object.registration_date,
                                            payment_period=object.subscription_period,
                                            payment_amount=object.amount)
                        payments.save()
                user = Member.objects.get(pk=id)
                gym_form = UpdateMemberGymForm(initial={
                                        'registration_date': user.registration_date,
                                        'registration_upto': user.registration_upto,
                                        'subscription_type': user.subscription_type,
                                        'subscription_period': user.subscription_period,
                                        'amount': user.amount,
                                        'fee_status': user.fee_status,
                                        'stop': user.stop,
                                        })

                info_form = UpdateMemberInfoForm(initial={
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        'dob': user.dob,
                                        })

                try:
                    payments = Payments.objects.filter(user=user)
                except Payments.DoesNotExist:
                    payments = 'No Records'
                messages.success(request, 'Cập nhật dự liệu thành công!')
                return redirect('update_member', id=user.pk)
            else:
                user = Member.objects.get(pk=id)
                info_form = UpdateMemberInfoForm(initial={
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        'dob': user.dob,
                                        })

                try:
                    payments = Payments.objects.filter(user=user)
                except Payments.DoesNotExist:
                    payments = 'No Records'
                return render(request,
                    'members/update_member.html',
                    {
                        'payments': payments,
                        'gym_form': gym_form,
                        'info_form': info_form,
                        'user': user,
                    })
    elif request.method == 'POST' and request.POST.get('info'):
        object = Member.objects.get(pk=id)
        object.first_name = request.POST.get('first_name')
        object.last_name = request.POST.get('last_name')
        object.dob = request.POST.get('dob')
        model_save(object)

        user = Member.objects.get(pk=id)
        gym_form = UpdateMemberGymForm(initial={
                                'registration_date': user.registration_date,
                                'registration_upto': user.registration_upto,
                                'subscription_type': user.subscription_type,
                                'subscription_period': user.subscription_period,
                                'amount': user.amount,
                                'fee_status': user.fee_status,
                                'stop': user.stop,
                                })

        info_form = UpdateMemberInfoForm(initial={
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'dob': user.dob,
                                })

        try:
            payments = Payments.objects.filter(user=user)
        except Payments.DoesNotExist:
            payments = 'No Records'
        
        return render(request,
            'members/update_member.html',
            {
                'payments': payments,
                'gym_form': gym_form,
                'info_form': info_form,
                'user': user,
                'updated': 'Record Updated Successfully',
            })
    else:
        user = Member.objects.get(pk=id)

        if len(Payments.objects.filter(user=user)) > 0:
            payments = Payments.objects.filter(user=user)
        else:
            payments = 'No Records'
        gym_form = UpdateMemberGymForm(initial={
                                'registration_date': user.registration_date,
                                'registration_upto': user.registration_upto,
                                'subscription_type': user.subscription_type,
                                'subscription_period': user.subscription_period,
                                'amount': user.amount,
                                'fee_status': user.fee_status,
                                'stop': user.stop,
                                })

        info_form = UpdateMemberInfoForm(initial={
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'dob': user.dob,
                                })
        return render(request,
                        'members/update_member.html',
                        {
                            'payments': payments,
                            'gym_form': gym_form,
                            'info_form': info_form,
                            'user': user,
                        }
                    )
    
def delete_member(request, id):
    print(id)
    Member.objects.filter(pk=id).delete()
    return redirect('view_member')

