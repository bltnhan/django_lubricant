from django.urls import path
from . import views
from home.dash_apps.finished_apps import part_1, part_1_1, part_2_1, part_2_2, part_2_3
from .views import home, login_view, logout_view, register_view, password_reset_request, \
	dashboard_1, dashboard_1_1, dashboard_2_1, dashboard_2_2, notice_contact, update_data, on_develope,dashboard_2_3
urlpatterns = [
	path('', home, name='homepage'),
	path('update/', update_data, name='update_data'),
	path('on_develope/', on_develope, name='develope'),
	path('index1/', dashboard_1, name='dashboard_1'),
	path('index1_1/',dashboard_1_1, name='dashboard_1_1'),
	path('index2_1/', dashboard_2_1, name='dashboard_2_1'),
	path('index2_2/', dashboard_2_2, name='dashboard_2_2'),
	path('index2_3/', dashboard_2_3, name='dashboard_2_3'),
	path('accounts/login/', login_view, name='login'),
	path('accounts/logout/', logout_view, name='logout'),
	path('accounts/register/', register_view, name='register'),
	path('accounts/password_reset_request/', password_reset_request, name='reset_password'),
	path('notice_contact/', notice_contact, name="notice"),
]