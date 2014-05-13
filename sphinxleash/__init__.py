import string
import six
import tempfile
import os
from sphinx import quickstart
from textwrap import dedent
from . import helpers
from .helpers import underline
from .version import __version__
import sys

quickstart_defaults = {
    # added to conf.py, and shows up in the footer by default
    'author': '',

    # create a windows .bat
    'batchfile': True,

    # add this to the beginning of static and template dirs
    'dot': '_',

    # epub support
    'epub': False,

    # create a makefile
    'makefile': True,

    # the name of the index.rst file
    'master': 'index',

    # where to create the new project.
    'path': '.',

    # project name
    'project': '',

    # release version
    'release': '',

    # full version
    'version': '',

    # separate build and source dirs
    'sep': False,

    # suffix to use for source files
    'suffix': '.rst',
}


class Project(object):
    def __init__(self, dirname, conf_dict=None, quickstart_params=None):
        """
        Represents a Sphinx documentation project.

        Parameters
        ----------
        dirname : str
            Directory that will be created and populated by sphinx-quickstart.

        conf_dict : dict
            Arbitrary dictionary that can be used to update the global
            variables in conf.py after it's been created.  Specifically, this
            adds the following line to the bottom of conf.py::

                globals().update(%s)\n" % str(conf_dict)

        quickstart_params : dict
            Dictionary of parameters to pass to sphinx-quickstart.  The
            available options and their defaults for this function are in the
            ``quickstart_defaults`` dictionary of this module.  The
            `quickstart_params` dictionary provided here will be used to update
            the default dictionary, so you only have to provide items that need
            to change.

        quiet : bool
        logfile : file-like object or None
            If None, let sphinx-quickstart print to stdout; otherwise,
            temporarily set stdout to this log file. This is useful for
            testing.

        """
        self.dirname = dirname
        self.conf_dict = conf_dict
        if quickstart_params is None:
            quickstart_params = {}
        self.quickstart_params = quickstart_params
        self.pages = {}

    def create_new(self, silent=True):
        """
        Calls sphinx.quickstart to populate a new project directory.

        Uses the currently-configured options in self.conf_dict and
        self.quickstart_params.
        """

        defaults = quickstart_defaults.copy()

        defaults['path'] = self.dirname
        defaults.update(self.quickstart_params)

        quickstart.generate(defaults, silent=silent)

        if defaults['sep']:
            self.source_dir = os.path.join(self.dirname, 'source')
        else:
            self.source_dir = self.dirname
        self.build_dir = os.path.join(
            self.dirname, '%sbuild' % defaults['dot'])
        if self.conf_dict is not None:
            self.conf_fn = os.path.join(self.source_dir, 'conf.py')
            helpers.update_conf(self.conf_fn, self.conf_dict)



    def add_page(self, template, filename, context=None, top=None, maxdepth=3,
                 preprocess=True):
        """
        Add a new :class:`Page`.

        Typically called by Project.add_page().

        Paramters
        ---------
        template : str
            ReST-formatted template, with format() style substitutions.  If
            you'll be including sub-pages, then it must have a `{TOC}`
            placeholder where the `.. toctree::` directive will be
            automatically filled in.

        filename : str
            Filename of the resulting *.rst file that will be created inside
            `dirname`.

        context : dict
            Dictionary of items to fill in.  If you've included placeholders in
            the `template`, then keys for those placeholders must be in this
            dictionary.

        top : str
            self.pages contains a dictionary of created pages; by setting `top`
            to one of these keys, the new Page will be added as a child to
            `top`.  If `top` is None, then the parent will be "index.rst".

        max_depth : int
            Maximum depth of table of contents

        preprocess : bool
            If True, then apply some formatting to the template by removing all
            shared whitespace ("dedenting"), and removing any blank lines at
            the top of the page.  Useful for when `template` is defined in
            a triple-quoted string.
        """

        if top is None:
            top = 'index.rst'

        dirname = self.source_dir

        p = Page(template, filename, dirname=dirname, context=context,
                 maxdepth=maxdepth)

        try:
            page = self.pages[top]
            page.add(p)
        except KeyError:
            pass

        self.pages[filename] = p
        return p

    def make(self, rules=['html']):
        """
        Run the Makefile with the rules indicated in `rules`.

        Parameters
        ----------
        rules : str or list
            Rules to run the Makefile with.  Call with `rules=None` or
            `rules=[]` to see output that will show what the options are.

        """
        if rules is None:
            rules = []
        if isinstance(rules, six.string_types):
            rules = [rules]
        cmds = [
            '(cd', self.dirname, '&&', 'make']
        cmds.extend(rules)
        cmds.append(')')
        os.system(' '.join(cmds))
        return self

    def show(self):
        """
        Show HTML version of the docs.
        """
        import webbrowser
        webbrowser.open_new_tab(
            os.path.join(self.build_dir, 'html', 'index.html'))
        return self

    def render(self):
        """
        Recursively render the currently configured pages.
        """
        self.pages['index.rst'].render()
        return self


class Page(object):
    def __init__(self, template, filename, context=None, dirname='.',
                 maxdepth=3, preprocess=True):
        """
        Represents a single ReST document.

        Typically called by Project.add_page().

        Paramters
        ---------
        template : str
            ReST-formatted template, with format() style substitutions.  If
            you'll be including sub-pages, then it must have a `{TOC}`
            placeholder where the `.. toctree::` directive will be
            automatically filled in.

        filename : str
            Filename of the resulting *.rst file that will be created inside
            `dirname`.

        dirname : str
            Dirname to create ReST file in.  This should be the source
            directory.  Typically a Page object is created by the Project.add
            method, which will automatically fill in the approprate `dirname`.

        context : dict
            Dictionary of items to fill in.  If you've included placeholders in
            the `template`, then keys for those placeholders must be in this
            dictionary.

        max_depth : int
            Maximum depth of table of contents

        preprocess : bool
            If True, then "dedent" the template by removing all shared
            whitespace, and remove any blank lines at the top of the page.
            Useful for when `template` is defined in a triple-quoted string.
        """

        self.maxdepth = maxdepth
        if preprocess:
            template = helpers.preprocess(template)
        self.template = template
        self.filename = filename
        self.dirname = dirname
        self.dest_fn = os.path.join(dirname, filename)
        self.toc = []
        if context is None:
            context = {}
        self.context = context

    def _fill_in_toc(self):
        if len(self.toc) == 0:
            return ""
        toc = ['.. toctree::']
        toc.append('    :maxdepth: %s' % self.maxdepth)
        toc.append('')
        for item in self.toc:
            item.render()
            toc.append('    ' + item.dest_relfn(self.dirname))
        return '\n'.join(toc)

    def dest_relfn(self, start):
        return os.path.relpath(self.dest_fn, start)

    def render(self):
        """
        Fills in the template placeholders and writes to file.
        """
        self.context['TOC'] = self._fill_in_toc()
        fout = open(self.dest_fn, 'w')
        template = string.Template(self.template)
        filled_in = template.safe_substitute(self.context).splitlines(False)
        if len(filled_in[0]) == 0:
            filled_in = filled_in[1:]
        fout.write('\n'.join(filled_in))
        fout.close()
        return self

    def add(self, others):
        """
        Add a single Page or iterable of Pages as children.

        Parameters
        ----------
        others : Page or iterable of Pages
        """
        if isinstance(others, Page):
            others = [others]
        for other in others:
            self.toc.append(other)
        return self

    def __repr__(self):
        return "<%s at %s>" % (self.__class__.__name__, self.dest_fn)


