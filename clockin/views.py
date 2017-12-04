from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from .models import *
from django.template import loader
from django.template.loader import render_to_string
from django.http import Http404
from django.forms import ModelForm
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy,reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.views.generic import TemplateView
import datetime
import calendar
from .filters import WorkListFilter
from .forms import WorkListFormHelper
from django.contrib.auth import logout
from dal import autocomplete
from django.db.models import Q
from django.views.generic.edit import UpdateView
from .filters import *
from django.conf import settings
from .config import *
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage
from django.db.models.functions import Concat
from django.db.models import Count



def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/clockin/')


#TGENERATES MAIN PAGE. TABLE. 
@login_required
def work_list(request):
	filter = Work.objects.filter(user=request.user).filter(active_session=True)

	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj.first()

	context = {
		'filter':filter,
		'name' : name,
	}

	if request.POST.get('mybtn'):
			ch = request.POST.get('checkbox','')
			#check to see if anything has been checked
			if not ch == '':
				url = reverse_lazy ('end_work_session', kwargs = {'work_id':ch})
				return HttpResponseRedirect(url)


	return render(request, 'timesheet/active_work_sessions.html', context)

#TGENERATES CURRENT SESSION PAGE. TABLE.
@login_required
def crt_session(request):
	filter = Work.objects.filter(user=request.user).filter(active_session=True)

	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj.first()

	context = {
		'filter':filter,
		'name' : name,
	}

###
	if request.POST.get('mybtn'):
			ch = request.POST.get('checkbox','')
			if not ch == '':
				url = reverse_lazy ('end_work_session', kwargs = {'work_id':ch})
				return HttpResponseRedirect(url)
###


	return render(request, 'timesheet/current_session.html', context)

def all_active(request):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')
	filter = Work.objects.filter(active_session=True)
	context = {
		'filter':filter,
	}
	
	return render(request, 'timesheet/all_active_sessions.html', context)

@login_required
def past_time(request):
	filter1 = Work.objects.filter(user=request.user).filter(active_session=False)
	intern_obj = Intern.objects.filter(username = request.user)
	userid = intern_obj[0].id
	name = intern_obj.first()
	form = PastLogsForm(request.POST or None)
	exp = Work.objects.all()
	exp=exp.filter(intern__exact=userid)

	if form.is_valid():
		year = int(form.cleaned_data['year'])
		month = int(form.cleaned_data['month'])
		pay_period = form.cleaned_data['pay_period']

		if month in range(1,13) and year in range(2015,datetime.date.today().year+1):
			if pay_period=='First Pay Period':
				start_date = datetime.date(year,month,1)
				end_date = datetime.date(year,month,15)
			elif pay_period=='Second Pay Period':
				start_date = datetime.date(year, month, 16)
				end_date = datetime.date(year, month, calendar.monthrange(year,month)[1])
			else:
				start_date = datetime.date(year, month, 1)
				end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])
			exp = exp.filter(date__range=(start_date, end_date))
		elif year in range(2015,(datetime.date.today().year)+1):
			start_date = datetime.date(year, 1, 1)
			end_date = datetime.date(year, 12, 31)
			exp = exp.filter(date__range=(start_date, end_date))

	context = {
		'name' : name,
		'form': form,
		'exp':exp,
	}

	return render(request, 'timesheet/past_time.html', context)

@login_required
#Clock in function
def add_new(request):
	form = ClockinForm(request.POST or None);
	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj.first()
	context = {
		'form' : form,
		'name' : name,
		'token' : SLACK_BOT_TOKEN,
	}
	if form.is_valid():
		obj = form.save(commit=False)
		obj.intern = intern_obj.first()

		obj.time_in = datetime.datetime.now().time()
		obj.active_session = True
		obj.user = request.user
		obj.duration = 0
		obj.save()
		url = reverse_lazy ('my_session')
		return HttpResponseRedirect(url)

	return render(request, 'timesheet/new_work_session.html', context)

@login_required
def clockout(request, work_id):
	instance = get_object_or_404(Work, id=work_id)
	form = ClockoutForm(request.POST or None, instance=instance)
	if (instance.active_session == False and not request.user.is_superuser) or (instance.user == request.user):
		return HttpResponseRedirect('/clockin/')
	intern_obj = Intern.objects.filter(username=request.user)
	name = intern_obj.first()

	if form.is_valid():
		obj = form.save(commit=False)
		obj.time_out = datetime.datetime.now().time()
		obj.active_session = False
		my_date = datetime.date.today()
		delta = datetime.datetime.combine(my_date,obj.time_out) - datetime.datetime.combine(my_date,obj.time_in)
	
		totalseconds = delta.total_seconds()
		hours = totalseconds/3600
		if hours > 8:
			obj.duration = 0
		elif hours < 0:
			new_hours = hours+24
			if new_hours > 8:
	 			new_hours = 0
			obj.duration = new_hours 
		else:
			obj.duration = hours
		obj.duration = float(obj.duration)
		obj.duration = round(obj.duration*4)/4
		obj.save()
		return HttpResponseRedirect('/clockin/')
	context = {
		'form' : form,
		'pk' : work_id,
		'name' : name,
		'token' : SLACK_BOT_TOKEN,
	}

	return render(request, 'timesheet/end_work_session.html', context)

@login_required
def edit_hours(request,work_id):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')
	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj.first()

	instance = get_object_or_404(Work, id=work_id)
	form = WorkForm(request.POST or None, instance=instance)
   

	if form.is_valid():
		obj = form.save(commit=False)
		obj.active_session = False
		my_date = datetime.date.today()

		delta = datetime.datetime.combine(my_date,obj.time_out) - datetime.datetime.combine(my_date,obj.time_in)
		totalseconds = delta.total_seconds()
		hours = totalseconds/3600
		if hours > 8:
			obj.duration = 0
		elif hours < 0:
			new_hours = hours+24
			obj.duration = new_hours 
		else:
			obj.duration = hours
		obj.duration = float(obj.duration)
		obj.duration = round(obj.duration*4)/4
		obj.save()

		return HttpResponseRedirect('/clockin/adminhome/')
	context = {
		'form' : form,
		'name' : name,
		'token' : SLACK_BOT_TOKEN,
		'pk' : work_id
	}

	return render(request, 'timesheet/edit_hours.html', context)

class workDelete(DeleteView):
	model = WorkForm
	success_url = reverse_lazy('adminhome')
	template_name = 'timesheet/delete_work_session.html'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(workDelete, self).get_context_data(**kwargs)
		# Add in a QuerySet of all the books
		context['token'] = SLACK_BOT_TOKEN
		return context


@login_required
#Clock in function
def add_work(request):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')
	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj.first()
	
	form = WorkForm(request.POST or None);
	obj = form.save(commit=False)
	context = {
		'form' : form,
		'token' : SLACK_BOT_TOKEN,
		'name' : name,
	}
	if form.is_valid():
		context = {
		'form' : form,
		'token' : SLACK_BOT_TOKEN,
		'name' : name,
		'user' : request.user,
	}
		obj.user = obj.intern.username
		obj.active_session = False

		my_date = datetime.date.today()

		delta = datetime.datetime.combine(my_date,obj.time_out) - datetime.datetime.combine(my_date,obj.time_in)
		totalseconds = delta.total_seconds()
		hours = totalseconds/3600
		if hours > 24 or hours < 0:
			obj.duration = 24
		else:
			obj.duration = hours
		obj.duration = float(obj.duration)
		obj.duration = round(obj.duration*4)/4
		obj.save()
		return HttpResponseRedirect('/clockin/adminhome/')

	return render(request, 'timesheet/admin_add_work_session.html', context)


class InternAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		qs = Intern.objects.all()
		if self.q:

			qs = (qs.filter(FName__istartswith=self.q) or qs.filter(LName__istartswith=self.q))
		return qs

#for implementing report generation functionality
@login_required
def adminhome(request):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')
	year=int(0)
	month=int(0)
	pay_period=""
	form = InternSummaryForm(request.GET or None)

	exp = Work.objects.all()

	print(form.is_valid())
	if form.is_valid():
		obj = form.save(commit=False)
		if obj.intern:
			user = obj.intern.username
			exp= Work.objects.filter(user__exact=user)
		year = int(form.cleaned_data['year'])
		month = int(form.cleaned_data['month'])
		pay_period = form.cleaned_data['pay_period']
		#email = form.cleaned_data['email']
		if month in range(1,13) and year in range(2015,datetime.date.today().year+1):
			if pay_period=='First Pay Period':
				start_date = datetime.date(year,month,1)
				end_date = datetime.date(year,month,15)
			elif pay_period=='Second Pay Period':
				start_date = datetime.date(year, month, 16)
				end_date = datetime.date(year, month, calendar.monthrange(year,month)[1])
			else:
				start_date = datetime.date(year, month, 1)
				end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])
			exp = exp.filter(date__range=(start_date, end_date))
		elif year in range(2015,(datetime.date.today().year)+1):
			start_date = datetime.date(year, 1, 1)
			end_date = datetime.date(year, 12, 31)
			exp = exp.filter(date__range=(start_date, end_date))


	exp1 = exp.values('intern_id','intern__FName','intern__LName').annotate(total=Sum('duration'))

	if request.GET.get('myemail'):
		html_message = loader.render_to_string('timesheet/get_report.html', {'exp':exp1})
		email = form.cleaned_data['email']
		send_mail('Intern Hours Summary', 'message', 'PMIClockin@gmail.com', [email], html_message=html_message)

	if request.POST.get('mybtn1'):
		che=request.POST.get('mybtn1')
		exp=exp.filter(intern__exact=che)
		month_name = calendar.month_name[month]
		return render(request, 'timesheet/intern_detail.html', context={'exp': exp,'pay_period':pay_period,'month':month_name,'year':year})

	if request.POST.get('mybtn'):
		ch = request.POST.get('checkbox','')
		if not ch == '':
			url = reverse_lazy ('edit_hours', kwargs = {'work_id':ch})
			return HttpResponseRedirect(url)

	return render(request, 'timesheet/admin_home.html',context = {'form': form,'exp':exp1})


