from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.configurator, name="configurator"),
    path("create_standard/", views.CreateStandardView.as_view(), name="create_standard"),
] 