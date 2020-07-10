import datetime
import os

from django.http import FileResponse
from django.shortcuts import render

from website import settings

# Create your views here.


basePath = settings.FILE_BROWSER_BASE_PATH
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


def getImg(request,path):
    full_path = os.path.join(basePath, path)
    file = open(full_path,'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="'+os.path.basename(path)+'"'
    return response

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
