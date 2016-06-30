import os
import mimetypes
import datetime

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from wsgiref.util import FileWrapper

from django.conf import settings


def path_inside_root(path, root):
    """True if path is the tree from root.
    Ej: path_inside_root("/foo/bar", "/foo") -> True
        path_inside_root("/bar/foo", "/foo") -> False
        path_inside_root("foo/bar", "foo/bar/else") -> True
    """
    abs_root, abs_path = os.path.abspath(root), os.path.abspath(path)
    common = os.path.commonprefix((abs_root, abs_path))
    return common.startswith(abs_root)

def _list_dir(path):
    try:
        _, dnames, fnames = os.walk(path).next()
    except StopIteration:
        raise Http404
    directories = []

    def get_attrs(name):
        stat = os.stat(os.path.join(path, name))
        return {"name": name, "stat": stat, "mtime": datetime.datetime.fromtimestamp(stat.st_mtime)}

    def remove_broken_symlinks(names):
        return [name for name in names if os.path.exists(os.path.join(path, name))]

    fnames = remove_broken_symlinks(fnames)
    files = map(get_attrs, sorted(fnames))
    dnames = remove_broken_symlinks(dnames)
    directories = map(get_attrs, sorted(dnames))

    context = {'directories': directories, 'files': files}
    return render_to_string('list_dir/list.html', context)

def list_dir(request, path):
    abspath = os.path.abspath(os.path.join(settings.LIST_DIR_ROOT, path))

    if not path_inside_root(abspath, settings.LIST_DIR_ROOT):
        raise Http404

    if os.path.isfile(abspath):
        mimetype = mimetypes.guess_type(abspath)[0]
        response = HttpResponse(FileWrapper(open(abspath)), content_type=mimetype)
        response['Content-Length'] = os.path.getsize(abspath)
        response['Content-Disposition'] = 'attachment'
        return response
    return render(request, "list_dir/list_base.html", {
        "list":_list_dir(abspath),
        "path": path,
    })
