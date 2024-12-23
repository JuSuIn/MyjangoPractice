from django.urls import path, re_path
from . import views
from . import converters

urlpatterns = [
    path("", view=views.index),
    path(route="archives/<date:release_date>/", view=views.index),
    re_path("^export\.(?P<format>(csv|xlsx))$", view=views.export),
    # path("export.csv", view=views.export_csv),
    path("<int:pk>/cover.png", view=views.cover_png),
]
