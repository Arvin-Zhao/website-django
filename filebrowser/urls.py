from django.urls import path


from . import views

urlpatterns = (
    path("", views.index, name="file_browser_index"),
    path("?path=<str:path>", views.index, name="file_browser_index"),
    path('?filesrc=<str:path>', views.get_file, name="file_browser_file_download"),
    path("?videoplaysrc=<str:path>", views.playvideo, name="file_browser_video_play"),
    path("?transcoding=<str:path>", views.transcode_video_page, name="file_browser_video_transcode")
)
