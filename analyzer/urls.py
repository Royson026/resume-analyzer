from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "history/",
        views.history,
        name="history"
    ),

    path(
        "history/delete/<int:analysis_id>/",
        views.delete_analysis,
        name="delete_analysis"
    ),

]