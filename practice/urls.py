from django.urls import path

from .views import RandomProblemView

urlpatterns = [
    path(
        "random-problem/",
        RandomProblemView.as_view(),
        name="random-problem",
    ),
]
