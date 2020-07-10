from django.urls import path


from . import views

urlpatterns = [
    path("", views.index, name="file_browser_index"),
    path("?path=<str:path>", views.index, name="file_browser_index"),
    path("?imgsrc=<str:path>", views.getImg, name="file_browser_img")
]
