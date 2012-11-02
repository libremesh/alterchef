import os
import mimetypes

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from django.http import Http404

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
    import datetime
    def get_attrs(name):
        stat = os.stat(os.path.join(path, name))
        return {"name": name, "stat": stat, "mtime": datetime.datetime.fromtimestamp(stat.st_mtime)}
    files = map(get_attrs, fnames)
    directories = map(get_attrs, dnames)

    context = {'directories': directories, 'files': files}
    return render_to_string('list_dir/list.html', context)

LIST_DIR_ROOT = "/home/san/somecode/altermeshfc/" # absolute path with trailing slash

def list_dir(request, path):
    abspath = os.path.abspath(os.path.join(LIST_DIR_ROOT, path))

    if not path_inside_root(abspath, LIST_DIR_ROOT):
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
