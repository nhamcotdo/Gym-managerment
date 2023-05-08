from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from .models import AddMemberForm, Member, SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def members(request):
    form = AddMemberForm()
    context = {
        'form': form,
        #'subs_end_today_count': get_notification_count(),
    }
    return render(request, 'members/add_member.html', context)

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
