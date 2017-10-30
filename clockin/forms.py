
from django import forms
from .models import Work, Intern
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineField, FormActions, StrictButton
from django.forms import extras
from dal import autocomplete
from. views import *
from django.core.validators import RegexValidator
class WorkForm(forms.ModelForm):

    class Meta:

        model = Work
        fields = ('intern', 'date','time_in', 'time_out', 'summary')
      
        widgets = {
          'date' : extras.SelectDateWidget(empty_label="Nothing"),
          'intern': autocomplete.ModelSelect2(url='intern-autocomplete')

        }

class WorkListFormHelper(FormHelper):    
    form_method = 'GET'
    field_template = 'bootstrap3/layout/inline_field.html'
    field_class = 'col-xs-3'
    label_class = 'col-xs-3'
    layout = Layout(
    	 Fieldset(
                    '<i class="fa fa-search"></i> Search Time Logs',       
                	'intern',
                  'date_between'
                ),
    			#'resource_first_name',
             	#'resource_last_name',
             	#'HUBzone',
             	#'employment_status',
              Submit('submit', 'Apply Filter'),
    ),


class ClockoutForm(forms.ModelForm):
    summary = forms.CharField( widget=forms.Textarea(attrs={'rows': 5, 'cols': 130,'placeholder': 'What work did you do today? (For payroll purposes)'}),validators=[RegexValidator(regex='^.{30,}$', message='The summary length has to be minimum 30 characters', code='nomatch')],label='')
    class Meta:

        model = Work
        fields = ('summary',)
        
class ClockinForm(forms.ModelForm):
    class Meta:

        model = Work
        fields = ()

#for report generation functionality
#YEAR_CHOICE=[('2010','2010'),('2011','2011'),('2012','2012'),('2013','2013'),('2014','2014'),('2015','2015'),('2016,'2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020')]
#YEAR_CHOICE= range(2010,2020)
MONTH_CHOICE=[('01','Jan'),('02','Feb'),('03','Mar'),('04','Apr'),('05','May'),('06','Jun'),('07','Jul'),('08','Aug'),('09','Sep'),('10','Oct'),('11','Nov'),('12','Dec')]
PAY_PERIOD=[('First Pay Period','First'),('Second Pay Period','Second')]

class EmailForm(forms.ModelForm):
     class Meta:
         model = Work
         fields = ('intern',)
         widgets = {
             'intern': autocomplete.ModelSelect2(url='intern-autocomplete')
         }
     month = forms.CharField(label = 'Month',widget=forms.Select(choices=MONTH_CHOICE))
     #year = forms.CharField(label = 'choose year',widget=forms.Select(choices=YEAR_CHOICE))
     #month = forms.CharField(label='choose month', widget=SelectDateWidget(years=range(1990, 2100)))
     pay_period = forms.CharField(label='Pay period',widget=forms.Select(choices=PAY_PERIOD))
     email=forms.EmailField()
     #Botcheck = forms.CharField(max_length=5)






#    class Meta:
 #       model = Person
  #      fields = ('__all__')


