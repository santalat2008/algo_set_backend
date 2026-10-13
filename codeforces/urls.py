from django.urls import path

from .views import CodeforcesConnectView

urlpatterns = [
    path("connect/", CodeforcesConnectView.as_view(), name="connect"),
]
