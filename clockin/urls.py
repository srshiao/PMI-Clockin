from django.conf.urls import url
from .models import *
from. import views
from django.views.generic.base import TemplateView
from .views import *

#app_name = 'clockin'

urlpatterns = [
    url(r'^$', views.work_list, name='index'),
    url(r'^home/$', views.work_list, name= 'home'),
    url(r'^current_session/$', views.crt_session, name= 'my_session'),
    url(r'^start_shift/$', views.add_new, name= 'add'),
    url(r'^edit/(?P<work_id>\d+)/$', views.clockout, name='end_work_session'),
    url(r'^admin_edit/(?P<pk>\d+)/delete/$', views.workDelete.as_view(model = Work), name="work_delete"),
    url(r'^adminhome/$', views.adminhome, name= 'adminhome'),
    url(r'^logout/$', views.logout_page, name = 'logout'),
    url(r'^history/$', views.past_time, name= 'past'),
    url(r'^admin_edit/(?P<work_id>\d+)/$', views.edit_hours, name='edit_hours'),
    url(r'^new_hours/$', views.add_work, name= 'add_work'),
    url(r'^intern-autocomplete/$',views.InternAutocomplete.as_view(),name='intern-autocomplete',),
	url(r'^active_interns/$', views.all_active, name= 'active_interns'),
    url(r'^adminhome/intern_detail/$', TemplateView.as_view(template_name='timesheet/intern_detail.html'), name='intern_detail'),

    






]
