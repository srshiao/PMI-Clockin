import django_filters
from .models import *
from django import forms
from dal import autocomplete
from django.db.models import Sum
import datetime


class WorkListFilter(django_filters.FilterSet):
	date_between = django_filters.DateFromToRangeFilter(name='date',label='Pay Period (MM/DD/YY)', widget=django_filters.widgets.RangeWidget())

	intern= django_filters.ModelChoiceFilter(name='intern', label='Intern',queryset=Intern.objects.all(), widget=autocomplete.ModelSelect2(url='intern-autocomplete'))

	class Meta:
		model = Work
		fields =  ('intern',)
		order_by = ['intern__FName']



MONTH_CHOICE=[('January','Jan'),('February','Feb'),('March','Mar'),('April','Apr'),('May','May'),('June','Jun'),('July','Jul'),('August','Aug'),('September','Sep'),('October','Oct'),('November','Nov'),('December','Dec')]
PAY_PERIOD=[('First Pay Period','First'),('Second Pay Period','Second')]

class ReportFilter(django_filters.FilterSet):
	#month = django_filters.CharFilter(label='choose month', widget=forms.Select(choices=MONTH_CHOICE))
	PAY_PERIOD = [('First Pay Period', 'First'), ('Second Pay Period', 'Second')]
	date_between = django_filters.DateFromToRangeFilter(name='date', label='Pay Period (MM/DD/YY)',
														widget=django_filters.widgets.RangeWidget(attrs={'placeholder': '2017/03/20'}))

	pay_period = forms.CharField(label='Pay_period', widget=forms.Select(choices=PAY_PERIOD))
	email = forms.EmailField()
	Botcheck = forms.CharField(max_length=5)
	intern = django_filters.ModelChoiceFilter(name='intern', label='Intern', queryset=Intern.objects.all())
	#review_object = Intern.object.values('intern').annotate(total=Sum('duration'))
	#class Meta:
		#model = Work
		#fields = ['intern',]
		#order_by = ['intern__FName']
         #widgets = {
         #    'intern': autocomplete.ModelSelect2(url='intern-autocomplete')
         #}




