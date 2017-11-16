
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
    summary = forms.CharField( widget=forms.Textarea(attrs={'rows': 5, 'cols': 130,'placeholder': 'What work did you do today? (For payroll purposes)'}),validators=[RegexValidator(regex='^.(?s).{30,}', message='The summary length has to be minimum 30 characters', code='nomatch')],label='')
    class Meta:

        model = Work
        fields = ('summary',)
        
class ClockinForm(forms.ModelForm):
    class Meta:

        model = Work
        fields = ()

MONTH_CHOICE=[('0','---'),('01','Jan'),('02','Feb'),('03','Mar'),('04','Apr'),('05','May'),('06','Jun'),('07','Jul'),('08','Aug'),('09','Sep'),('10','Oct'),('11','Nov'),('12','Dec')]
PAY_PERIOD=[('First Pay Period','First'),('Second Pay Period','Second'),('Both Pay Periods ','Both')]

class InternSummaryForm(forms.ModelForm):
     class Meta:
         model = Work
         fields = ('intern',)
         widgets = {
             'intern': autocomplete.ModelSelect2(url='intern-autocomplete')
         }
     month = forms.CharField(required=False,label = 'Month',widget=forms.Select(choices=MONTH_CHOICE))
     pay_period = forms.CharField(label='Pay period',widget=forms.Select(choices=PAY_PERIOD))
     email=forms.CharField(label='Email',required=False)



