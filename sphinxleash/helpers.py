import re
from six.moves import html_entities
import sys
import os
import base64
import mimetypes
from textwrap import dedent, wrap


def rest_table(items, header=True):
    """
    Given an iterable-of-iterables, return a reStructured Text table.

    Thanks http://stackoverflow.com/questions/11347505/
    """
    def fix(x):
        return str(x).replace('\n', ' ')
    items = [list(map(fix, i)) for i in items]
    ncols = set([len(i) for i in items])
    if len(ncols) != 1:
        raise ValueError(
            "Inconsistent number of cells. Rows with %s cells found" % ncols)
    ncols = list(ncols)[0]
    colsizes = [
        max(len(r[i]) for r in items) for i in range(ncols)]
    formatter = ' '.join('{:<%d}' % c for c in colsizes)
    rows_formatted = [formatter.format(*row) for row in items]
    divider = formatter.format(*['=' * c for c in colsizes])
    output = []
    output.append(divider)
    if header:
        output.append(rows_formatted.pop(0))
        output.append(divider)
    output.extend(rows_formatted)
    output.append(divider)
    return '\n'.join(output)


def indent(t, indentation='    '):
    s = []
    for i in t.splitlines(True):
        s.append(indentation + i)
    return ''.join(s)


def get_path_url(abs_path, relative=False):
    """ Returns an absolute or relative path url from an absolute path.
    """
    if relative:
        return get_rel_path_url(abs_path)
    else:
        return get_abs_path_url(abs_path)


def get_rel_path_url(path, base_path=os.getcwd()):
    """ Returns a relative path from the absolute one passed as argument.
        Silently returns originally provided path on failure.
    """
    try:
        path_url = path.split(base_path)[1]
        if path_url.startswith('/'):
            return path_url[1:]
        else:
            return path_url
    except (IndexError, TypeError):
        return path


def encode_image_from_url(url, source_path):
    if (
        not url
        or url.startswith('data:')
        or url.startswith('file://')
        or url.startswith('http://')
        or url.startswith('https://')
    ):
        return url

    real_path = url if os.path.isabs(url) else os.path.join(source_path, url)

    if not os.path.exists(real_path):
        return url

    mime_type, encoding = mimetypes.guess_type(real_path)

    if not mime_type:
        return url

    try:
        with open(real_path, 'rb') as image_file:
            image_contents = image_file.read()
            encoded_image = base64.b64encode(image_contents)
    except IOError:
        return url
    except Exception:
        return url

    return "data:%s;base64,%s" % (mime_type, encoded_image.decode())


def embed_images(source, dest):
    content = open(source).read()
    images = re.findall(r'<img\s.*?src="(.+?)"\s?.*?/?>', content,
                        re.DOTALL | re.UNICODE)
    source_dir = os.path.dirname(source)
    for image_url in images:
        encoded_url = encode_image_from_url(image_url, source_dir)
        if encoded_url is None:
            continue
        content = content.replace("src=\"" + image_url,
                                  "src=\"" + encoded_url, 1)
    with open(dest, 'w') as fout:
        fout.write(content)


def preprocess(s):
    s = dedent(s)
    lines = s.splitlines(False)
    fixed = []
    content = False
    for line in lines:
        if len(line) == 0 and not content:
            continue
        else:
            content = True
            fixed.append(line)
    return '\n'.join(fixed)


def update_conf(conf, d):
    """
    Updates conf.py based on the values in dict `d`.
    """
    # Thanks https://groups.google.com/forum/#!topic/sphinx-users/zpxYWULf_Rs
    orig = open(conf).read()
    add = "globals().update(%s)\n" % str(d)
    imports = d.pop('imports', None)
    with open(conf, 'w') as fout:
        if imports is not None:
            if not isinstance(imports, list):
                imports = [imports]
            for imp in imports:
                fout.write(imp + '\n')
        fout.write(orig)
        fout.write(add)


def underline(s, symbol='='):
    """
    Add an underline to the string `s`.

    Parameters
    ----------
    s : str
        String to use for the title

    symbol : str
        Character to use for the underline
    """
    return '\n'.join([s, symbol * len(s)])
