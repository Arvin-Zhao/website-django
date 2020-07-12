import datetime
import os
import threading

from django.http import FileResponse
from django.shortcuts import render

from website import settings
import ffmpeg_streaming
# Create your views here.


basePath = settings.FILE_BROWSER_BASE_PATH
transcode_dic = {}
if not os.path.isdir(basePath):
    raise NotADirectoryError(basePath)


def index(request, path='', sort='Name'):
    if len(path) > 2 and path[-2:] == '..':
        path = str.join('\\', path.split('\\')[:len(path.split('\\'))-2])
    full_path = os.path.join(basePath, path)

    dir_info = [PathInfoFactory.create(os.path.join(full_path, x)) for x in os.listdir(full_path)]
    if path:
        dir_info.insert(0, PathDirInfo(os.path.join(basePath, "..")))
    return render(request, "filebrowser/index.html", {"dir_info": dir_info, "sort": sort, "path":path})


def get_file(request, path):
    full_path = os.path.join(basePath, path)
    file = open(full_path,'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="'+os.path.basename(path)+'"'
    return response


def transcode_video(path):
    if path in transcode_dic:
        return transcode_dic[path]

    transcode_dic[path] = 0
    path_folder = os.path.dirname(path)
    file_name = os.path.basename(path)
    play_path = os.path.join(path_folder, get_play_file_name(file_name))

    video = ffmpeg_streaming.input(path)
    hls = video.hls(ffmpeg_streaming.Formats.h264())

    def monitor(ffmpeg, duration, time_, time_left, process):
        transcode_dic[path] = round(time_ / duration * 100)

    _1080p = ffmpeg_streaming.Representation(ffmpeg_streaming.Size(1920, 1080), ffmpeg_streaming.Bitrate(4096 * 1024, 320 * 1024))
    hls.representations(_1080p)
    thread = threading.Thread(target=(lambda: hls.output(play_path, monitor=monitor,
                                                         text=True, encoding="utf-8", async_run=True)))
    thread.start()

    return transcode_dic[path]


def transcode_video_page(request, path):
    full_path = os.path.join(basePath, path)
    percent = transcode_video(full_path)

    path_folder = os.path.dirname(path)
    file_name = os.path.basename(path)
    play_path = os.path.join(basePath, path_folder, get_play_file_name(file_name, "_1080p"))
    if percent == 100 and os.path.exists(play_path):
        return playvideo(request, path)

    return render(request, "filebrowser/video_transcoding.html", {"percent": percent})


def playvideo(request, path):
    path_folder = os.path.dirname(path)
    file_name = os.path.basename(path)
    play_path = os.path.join(basePath, path_folder, get_play_file_name(file_name, "_1080p"))
    if not os.path.exists(play_path):
        return transcode_video_page(request, path)

    return render(request, "filebrowser/video_play.html", {
        "file_name": file_name[:file_name.rindex(os.path.extsep)]+".m3u8",
        "file_src": path_folder
    })


def get_play_file_name(file_name, bit=""):
    return os.path.join(".play", file_name[:file_name.rindex(os.path.extsep)]+bit+".m3u8")


class PathInfoFactory:
    @staticmethod
    def create(path):
        if not os.path.lexists(path):
            raise FileNotFoundError(path)

        if os.path.isdir(path):
            return PathDirInfo(path)
        elif os.path.isfile(path):
            return PathFileInfo(path)
        elif os.path.islink(path):
            return PathLinkInfo(path)


class PathInfo:

    def __init__(self, path):
        if not os.path.lexists(path):
            raise FileNotFoundError(path)
        self.CreatedAt = datetime.datetime.fromtimestamp(os.path.getctime(path))
        self.UpdatedAt = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        self.AccessedAt = datetime.datetime.fromtimestamp(os.path.getatime(path))
        self.IsFile = os.path.isfile(path)
        self.IsDir = os.path.isdir(path)
        self.IsLink = os.path.islink(path)
        self.Name = os.path.basename(path)

    def __str__(self):
        """

        :rtype: str
        """
        return self.Name


class PathDirInfo(PathInfo):
    def __init__(self, path):
        super(PathDirInfo, self).__init__(path)
        self.Type = "Folder"


class PathFileInfo(PathInfo):
    def __init__(self, path):
        super(PathFileInfo, self).__init__(path)
        self.FileSize = os.path.getsize(path)
        self.Type = self.Name.split(os.path.extsep)[-1]


class PathLinkInfo(PathInfo):
    def __init__(self, path):
        super(PathLinkInfo, self).__init__(path)
        self.Type = "Link"
