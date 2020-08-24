from django.urls import path

from . import views

urlpatterns = [
    path("confirm/<uuid:worklog_uuid>", views.confirm, name="confirm"),
]
