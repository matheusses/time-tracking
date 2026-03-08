from django.urls import path

from . import views

app_name = "tracking"
urlpatterns = [
    path("", views.home, name="home"),
    path("timer/", views.timer_partial, name="timer_partial"),
    path("timer/start/", views.start_timer, name="timer_start"),
    path("timer/stop/", views.stop_timer, name="timer_stop"),
    path("timesheet/", views.timesheet_page, name="timesheet"),
    path("timesheet/grid/", views.timesheet_grid_partial, name="timesheet_grid"),
    path("timesheet/update/", views.update_time_entry, name="timesheet_update"),
]
