from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('api/data/', views.calendar_data, name='calendar_data'),
    path('api/day/<int:year>/<int:month>/<int:day>/', views.day_details, name='day_details'),
    path('api/set-active-group/', views.set_active_group, name='set_active_group'),
]
