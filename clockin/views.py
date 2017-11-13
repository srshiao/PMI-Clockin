from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.template import loader
from django.http import Http404
from django.forms import ModelForm
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.views.generic import TemplateView
import datetime
from .filters import WorkListFilter
from .forms import WorkListFormHelper
from django.contrib.auth import logout
from dal import autocomplete
from django.db.models import Q
from django.views.generic.edit import UpdateView
from .filters import *
from django.conf import settings
from .config import *


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/clockin/')


#TGENERATES MAIN PAGE. TABLE. 
@login_required
def work_list(request):
#	if request.user.is_superuser:
#		return HttpResponseRedirect('/clockin/adminhome')
	filter = Work.objects.filter(user=request.user).filter(active_session=True)

	intern_obj = Intern.objects.filter(username = request.user)
	#name = intern_obj[0]
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


	return render(request, 'timesheet/active_work_sessions.html', context)

#TGENERATES CURRENT SESSION PAGE. TABLE. 
@login_required
def crt_session(request):
#	if request.user.is_superuser:
#		return HttpResponseRedirect('/clockin/adminhome')
	filter = Work.objects.filter(user=request.user).filter(active_session=True)

	intern_obj = Intern.objects.filter(username = request.user)
	#name = intern_obj[0]
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



@login_required
def past_time(request):
	filter1 = Work.objects.filter(user=request.user).filter(active_session=False)

	intern_obj = Intern.objects.filter(username = request.user)
	#name = intern_obj[0]
	name = intern_obj.first()

	context = {
		'filter1':filter1,
		'name' : name,
	}

	return render(request, 'timesheet/past_time.html', context)

@login_required
#Clock in function
def add_new(request):
	form = ClockinForm(request.POST or None);
	intern_obj = Intern.objects.filter(username = request.user)
	#name = intern_obj[0]
	name = intern_obj.first()
	context = {
		'form' : form,
		'name' : name,
		'token' : SLACK_BOT_TOKEN,
	}
	if form.is_valid():
		obj = form.save(commit=False)
		#obj.intern = intern_obj[0]
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
	intern_obj = Intern.objects.filter(username = request.user)
	#name = intern_obj[0]
	name = intern_obj.first()

	if form.is_valid():
		obj = form.save(commit=False)
		obj.time_out = datetime.datetime.now().time()
		obj.active_session = False
		my_date = datetime.date.today()

		delta = datetime.datetime.combine(my_date,obj.time_out) - datetime.datetime.combine(my_date,obj.time_in)
	
		totalseconds = delta.total_seconds()
		hours = totalseconds/3600
		if hours > 9:
			obj.duration = 0
		elif hours < 0:
			new_hours = hours+24
			if new_hours > 9:
	 			new_hours = 0
			obj.duration = new_hours 
		else:
			obj.duration = hours
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
def AdminView(request):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')
	f = WorkListFilter(request.GET,queryset = Work.objects.filter(active_session=False))

	context = {
		'filter': f,
	}

	###
	if request.POST.get('mybtn'):
			ch = request.POST.get('checkbox','')
			if not ch == '':
				url = reverse_lazy ('edit_hours', kwargs = {'work_id':ch})
				return HttpResponseRedirect(url)
	###


	return render(request, 'timesheet/all_work_sessions.html', context)

@login_required
def edit_hours(request,work_id):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')

	instance = get_object_or_404(Work, id=work_id)
	form = WorkForm(request.POST or None, instance=instance)
   

	if form.is_valid():
		obj = form.save(commit=False)
		obj.active_session = False
		my_date = datetime.date.today()

		delta = datetime.datetime.combine(my_date,obj.time_out) - datetime.datetime.combine(my_date,obj.time_in)
		totalseconds = delta.total_seconds()
		hours = totalseconds/3600
		if hours > 9:
			obj.duration = 0
		elif hours < 0:
			new_hours = hours+24
			obj.duration = new_hours 
		else:
			obj.duration = hours
		obj.save()

		return HttpResponseRedirect('/clockin/adminhome')
	context = {
		'form' : form,
		'pk' : work_id
	}

	return render(request, 'timesheet/edit_hours.html', context)





#NOT USED

#Don't worry about this one. 
#def index(request):
#	table = WorkTable(Work.objects.all())
#	context = {
#		'table': table,
#
#	}
#
#	RequestConfig(request).configure(table)
#	return render(request, 'timesheet/active_work_sessions.html', context)
class workDelete(DeleteView):
	model = WorkForm
	success_url = reverse_lazy('adminhome')
	template_name = 'timesheet/delete_work_session.html'


@login_required
#Clock in function
def add_work(request):
	form = WorkForm(request.POST or None);
	context = {
		'form' : form
	}
	if form.is_valid():
		obj = form.save(commit=False)
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
		obj.save()
		return HttpResponseRedirect('/clockin/')

	return render(request, 'timesheet/admin_add_work_session.html', context)


class InternAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		#qs = Intern.objects.order_by('FName').distinct()
		qs = Intern.objects.all()
		if self.q:
		#qs = qs.filter(FName__exact='Sam')

			qs = (qs.filter(FName__istartswith=self.q) or qs.filter(LName__istartswith=self.q))
		return qs

#not in current use. will be used as a Constituent Details Page
#@login_required
#def detail(request, work_id):
#	try:
#		person = Work.objects.get(pk=work_id)
#	except Work.DoesNotExist:
#		raise Http404("Log does not exist")
#	return render(request, 'timesheet/detail.html', {'employee': person})


