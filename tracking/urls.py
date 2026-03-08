from django.urls import path

from . import views

app_name = "tracking"
urlpatterns = [
    path("", views.home, name="home"),
    path("timer/", views.timer_partial, name="timer_partial"),
    path("timer/start/", views.start_timer, name="timer_start"),
    path("timer/stop/", views.stop_timer, name="timer_stop"),
]
