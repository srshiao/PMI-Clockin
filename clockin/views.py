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
#from django.core.mail.MIMEMultipart import MIMEMultipart
#		from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/clockin/')


#TGENERATES MAIN PAGE. TABLE. 
@login_required
def work_list(request):
	if request.user.is_superuser:
		return HttpResponseRedirect('/clockin/adminhome')
	filter = Work.objects.filter(user=request.user).filter(active_session=True)

	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj[0]
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

@login_required
def past_time(request):
	filter1 = Work.objects.filter(user=request.user).filter(active_session=False)

	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj[0]
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
	name = intern_obj[0]
	context = {
		'form' : form,
		'name' : name,
		'token' : SLACK_BOT_TOKEN,
	}
	if form.is_valid():
		obj = form.save(commit=False)
		obj.intern = intern_obj[0]
		obj.time_in = datetime.datetime.now().time()
		obj.active_session = True
		obj.user = request.user
		obj.duration = 0
		obj.save()
		return HttpResponseRedirect('/clockin/')

	return render(request, 'timesheet/new_work_session.html', context)

@login_required
def clockout(request, work_id):
	instance = get_object_or_404(Work, id=work_id)
	form = ClockoutForm(request.POST or None, instance=instance)
	intern_obj = Intern.objects.filter(username = request.user)
	name = intern_obj[0]
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

#The original adminhome page. Currently not used

#@login_required
#def AdminView(request):
#	if not request.user.is_superuser:
#		return HttpResponseRedirect('/clockin/')
#	f = WorkListFilter(request.GET,queryset = Work.objects.filter(active_session = False))
#	context = {
#		'filter': f,
#	}

	###
#	if request.POST.get('mybtn'):
#			ch = request.POST.get('checkbox','')
#			if not ch == '':
#				url = reverse_lazy ('edit_hours', kwargs = {'work_id':ch})
#				return HttpResponseRedirect(url)
#	if request.POST.get('report'):
#		#html_message = loader.render_to_string('timesheet/get_report.html', {'filter': f})
#		url_one = reverse_lazy('email')
#		return HttpResponseRedirect(url_one)
#	return render(request, 'timesheet/all_work_sessions.html', context)

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
	success_url = reverse_lazy('email')
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

#for implementing report generation functionality
@login_required
def sendmail(request):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/clockin/')
	form = InternSummaryForm(request.POST or None)
	exp = Work.objects.all()
	#print(form.is_valid())
	if form.is_valid():
		obj = form.save(commit=False)
		if obj.intern:
			user = obj.intern.username
			exp= Work.objects.filter(user__contains=user)
		year = datetime.date.today().year
		month = int(form.cleaned_data['month'])
		pay_period = form.cleaned_data['pay_period']
		#email = form.cleaned_data['email']
		if month in range(1,12):
			if pay_period=='First Pay Period':
				start_date = datetime.date(year,month,1)
				end_date = datetime.date(year,month,15)
				exp = exp.filter(date__range=(start_date,end_date))
			elif pay_period=='Second Pay Period':
				start_date = datetime.date(year, month, 16)
				end_date = datetime.date(year, month, calendar.monthrange(year,month)[1])
				exp = exp.filter(date__range=(start_date, end_date))
			elif pay_period=='Both Pay Periods':
				start_date = datetime.date(year, month, 1)
				end_date = datetime.date(year, month, calendar.monthrange(year, month)[1])
				exp = exp.filter(date__range=(start_date, end_date))

	exp1 = exp.values('intern_id','intern__FName','intern__LName').annotate(total=Sum('duration'))#sum=Concat('summary','user'))
	#print (exp1)
	if request.POST.get('myemail'):
		#return HttpResponse("yes success")
				#review_object = Work.objects.values('intern').annotate(total=Sum('duration'))
		#html_message = loader.render_to_string('timesheet/get_report.html', {'exp':exp1})
		email = form.cleaned_data['email']
		html_message = loader.get_template('timesheet/get_report.html').render({'exp':exp1})
		send_mail('Test email', 'message', 'PMIClockin@gmail.com', [email],html_message=html_message)


		#text_content = 'This is an important message.'
		#html_content = loader.get_template('timesheet/get_report.html').render( {'exp': exp1})
		#msg = EmailMultiAlternatives("Using EmailMultiAlternatives method", text_content,'PMIClockin@gmail.com' , [email])
		#msg.attach_alternative(html_content, "text/html")
		#msg.send()
		# To implement html formatting in the mail body

		# Create the root message and fill in the from, to, and subject headers
		#msg_root = MIMEMultipart('related')
		#msg_root.preamble = 'This is a multi-part message in MIME format.'

		# Encapsulate the plain and HTML versions of the message body in an
		# 'alternative' part, so message agents can decide which they want
		# to display.
		#msg_alternative = MIMEMultipart('alternative')
		#msg_root.attach(msg_alternative)

		# Attach HTML and text alternatives.

		#msg_text = MIMEText(html_content.encode('ascii'), 'html', _charset='ascii')
		#msg_alternative.attach(msg_text)
		#send_mail('Test email', msg_root.as_string(), 'PMIClockin@gmail.com', [email])
		#print (msg_root.as_string().encode('ascii'))
		#smtp.sendmail(from_addr, to_addrs, msg_root.as_string())
		#smtp.close()

	if request.POST.get('mybtn1'):
		#print (1234)
		#return HttpResponse("yes success")
		che=request.POST.get('mybtn1')
		#print (che)
		exp=exp.filter(intern__exact=che)
		#form1 = EmailForm(request.POST or None)
		#dummy = list(exp.values())
		#request.session['dummy'] = dummy
		#url = reverse_lazy('thankyou', args=(exp,))
		month_name = calendar.month_name[month]
		if month:
			return render(request, 'timesheet/intern_detail.html', context={'exp': exp,'pay_period':pay_period,'month':month_name})
		else:
			return render(request, 'timesheet/intern_detail_all.html', context={'exp': exp})
	if request.POST.get('mybtn'):
		ch = request.POST.get('checkbox','')
		if not ch == '':
			url = reverse_lazy ('edit_hours', kwargs = {'work_id':ch})
			return HttpResponseRedirect(url)

		#return('intern_detail')
		#return HttpResponseRedirect('/clockin/email/intern_detail/')
	#	temp= print(exp1[0])

						#return HttpResponseRedirect('/clockin/email/thankyou/')
				#except:
				#return HttpResponseRedirect('/email/')
		#else:
			#return HttpResponseRedirect('/email/')

	return render(request, 'timesheet/email.html',context = {'form': form,'exp':exp1})







	#not in current use. will be used as a Constituent Details Page
#@login_required
#def detail(request, work_id):
#	try:
#		person = Work.objects.get(pk=work_id)
#	except Work.DoesNotExist:
#		raise Http404("Log does not exist")
#	return render(request, 'timesheet/detail.html', {'employee': person})


