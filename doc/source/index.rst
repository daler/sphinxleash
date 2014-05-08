.. sphinxlite documentation master file, created by
   sphinx-quickstart on Fri May  2 12:03:14 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. role:: raw-html(raw)
    :format: html

``sphinxleash``
===============

`Sphinx <http://sphinx-doc.org/>`_ is a wonderful tool for writing
documentation.

But imagine a situation where we want to write a report on results from an
experiment.  We might have a page for each sample, with the same format for
each of these pages but with different actual content.  Using Sphinx alone, we
would have to manually copy/paste text in reST documents to populate the pages
for each sample.

:mod:`sphinxleash` solves this by allowing the user to guide Sphinx
documentation generation from within Python code, instead of a combination of
commands in the terminal and editing text files.  The workflow is:

1. Create a new project
2. Write reST templates (plain strings) for each page, with placeholders for
   content
3. Fill in the placeholders with content and connect the pages together
4. Render and view

Below is the code to create two projects: a simple one with mostly default
settings and minimal text, just to give an idea of the workflow, and a second,
more complex one with customization (Bootstrap theme, custom CSS, custom Sphinx
extensions) and more content (images, tables).

Here are the end products:

* :raw-html:`<a href="simple-example/index.html">Simple example</a>`
* :raw-html:`<a href="advanced-example/index.html">Advanced example</a>`

Installation
------------

Simply::

    pip install sphinxleash

Alternatively, the `development version on github <https://github.com/daler/sphinxleash>`_
always has the latest code.

To run the :ref:`advanced-example`, you will also need ``matplotlib`` and
``sphinx_bootstrap_theme``, but these are not required for :mod:`sphinxleash`
itself.


.. _simple-example:

Simple example
--------------

.. testcode::
    :hide:

    import os
    if os.path.exists('simple-example'):
        os.system('rm -r simple-example')
    if os.path.exists('advanced-example'):
        os.system('rm -r advanced-example')

    import matplotlib
    matplotlib.use("Agg")


Create a new project
~~~~~~~~~~~~~~~~~~~~
First, let's configure and initialize a project:

.. testcode::

    import sphinxleash
    project = sphinxleash.Project(dirname='simple-example')
    project.create_new()

.. testoutput::

    Creating file simple-example/conf.py.
    Creating file simple-example/index.rst.
    Creating file simple-example/Makefile.
    Creating file simple-example/make.bat.


Write templates
~~~~~~~~~~~~~~~

Next, we need to construct the strings that will serve as templates for the
pages.  The string is any valid reStructuredText.  By default, any leading
blank lines and all common whitespace at the beginning of each line will be
stripped, so you can write these templates as triple-quoted strings in normal
Python code.

Each template can contain any number of ``$``-based placeholders, used in
:class:`string.Template` objects (see the `Python docs
<https://docs.python.org/2/library/string.html#template-strings>`_ for more on
this).

For example, if ``$sample`` is in the template, then we can provide
a dictionary ``d`` and the value of ``d["sample"]`` will substituted for the
placeholder.

There's one special placeholder, ``$TOC``.  It must be present to use the
Sphinx-specific `toctree directive
<http://sphinx-doc.org/markup/toctree.html>`_ that links together multiple reST
documents.  :mod:`sphinxleash` fills this in automatically; the placeholder
just needs to be somewhere in the template.

Here are our templates -- one for the index page, and one for sample pages:

.. testcode::

    index_template = """
    Simple example
    ==============

    This is the index page.

    Table of contents
    -----------------

    $TOC
    """

    # The title and sample number will be filled in later
    page_template = """
    $title
    This is the page for sample $number.

    $TOC
    """


Connect the pages together
~~~~~~~~~~~~~~~~~~~~~~~~~~
Now we use the :meth:`Project.add_page` method to populate the project with
reST templates, each filled in with different `context` dictionaries.

The :file:`index.rst` page is special for Sphinx, and always has to exist.  So
it's a good idea to make it first.  Our template for the index doesn't have any
custom placeholders, so all we have to do is specify the template and the
filename.  The `project` object will figure out the source directory of the
project, and save :file:`index.rst` in the right place:

.. testcode::

    # First the top-level index page
    project.add_page(index_template, 'index.rst')

Let's make some more pages.  For each page, we're making a new ``context``
dictionary which will be used to fill in the placeholders for the
``page_template``.

.. testcode::

    for n in range(10):

        # Helper function for making reST titles with underlines
        title = sphinxleash.underline('Sample %s' % n, symbol="=")

        project.add_page(
            page_template,
            filename='page%s.rst' % n,
            context=dict(title=title, number=n)
        )



Render and view
~~~~~~~~~~~~~~~
At this point, no files have actually been created on disk yet.  We've simply
told :mod:`sphinxleash` how to connect pages together and how to fill in their
content.  To actually do this, we need to call the :meth:`Project.render`
method:

.. testcode::

    # Write the configured .rst files to the project directory
    project.render()

Sphinx projects use a Makefile to build the docs, but for convenience this is
wrapped by :mod:`sphinxleash`.  Here we clean the build and then build the HTML
version:

.. testcode::

    project.make(['clean', 'html'])

For HTML docs, we can use the :meth:`Project.show` method to open a web browser
to show the docs:

.. testcode::

    project.show()

Alternatively, we could chain these steps together:

.. testcode::

    # Render, make, show all at once
    project.render().make(['clean', 'html']).show()


Take a look at the :raw-html:`<a href="simple-example/index.html">final product</a>`.

.. _advanced-example:

Advanced example
----------------

Overview
~~~~~~~~
This is a considerably more advanced example.  To replicate it, you'll need to
have `matplotlib <http://matplotlib.org/>`_ (for figure-making) and
`sphinx_bootstrap_theme
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html>`_ installed.
This example includes:

- using the ``sphinx_bootstrap_theme`` and setting theme options in the
  :file:`conf.py` file generated by Sphinx
- customizing the Jinja HTML layout template
- adding custom CSS styles
- sample pages, each with a sub-page for a figure and a sub-page for a table
  showing the data

First, make sure you can import these:

.. testcode::

    import sphinxleash
    import sphinx_bootstrap_theme
    from matplotlib import pyplot as plt
    import numpy as np


Create a new project
~~~~~~~~~~~~~~~~~~~~
As in the :ref:`simple-example`, we configure a new :class:`Project`.  The
``config_dict`` argument is used to override variables in the :file:`conf.py`
file generated by Sphinx.  We will use this to make some changes as documented
in the `sphinx_bootstrap_theme docs
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html#customization>`_
for using the Bootstrap theme.

We can also specify additional arguments to ``sphinx-quickstart`` using the
``quickstart_params`` argument.  If you've run ``sphinx-quickstart`` from the
command line, these parameters are the answers to all the questions it asks you
interactively.  Here, we're just setting the author name, but other options can
be found by inspecting the :attr:`sphinxleash.quickstart_defaults` dictionary.

As before, at the end we call :meth:`Project.create_new` to actually create the
files.  This method also does the in-place modification of :file:`conf.py`
after it's initially created.

.. testcode::

    project = sphinxleash.Project(
        dirname="advanced-example",

        # Variables to override in conf.py
        conf_dict=dict(
            html_theme='bootstrap',
            html_theme_path=sphinx_bootstrap_theme.get_html_theme_path(),
            html_theme_options=dict(
                navbar_title='sphinxleash advanced example',
                bootswatch_theme='united'
            ),
            html_static_path=['_static'],
            templates_path=['_templates'],
        ),

        # Only make a small change in the quickstart config
        quickstart_params=dict(author='Made by sphinxleash'),
    )

    # Populate the project with initial files, and make overrides to conf.py
    project.create_new()

.. testoutput::

    Creating file advanced-example/conf.py.
    Creating file advanced-example/index.rst.
    Creating file advanced-example/Makefile.
    Creating file advanced-example/make.bat.

Layout and CSS customization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now we're going to make some changes to the layout, as documented `here
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html#extending-layout-html>`_.
We can use the :attr:`project.source_dir` attribute to get the source directory
correct:

.. testcode::

    from textwrap import dedent
    with open(os.path.join(project.source_dir, '_templates', 'layout.html'), 'w') as fout:
        fout.write(dedent(
        """
        {% extends "!layout.html" %}
        {% set bootswatch_css_custom = ['_static/style.css'] %}
        """))

Next, we add some custom CSS, as documented `here
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html#adding-custom-css>`_.
This changes the footer text color (to make a visibly obvious change) and also
makes some tweaks to how figures and figure captions will be displayed. Note
that the path for this CSS file, relative to the project source dir (available
as :attr:`project.source_dir`) needs to match what we set for the
``bootswatch_css_custom`` line in :file:`layout.html` above.

.. testcode::

    with open(os.path.join(project.source_dir, '_static', 'style.css'), 'w') as fout:
        fout.write(dedent(
            """
            footer {
                color: blue;
            }

            p.caption {
                font-style: italic;
                font-size: 80%;
            }

            div.figure {
                width: 540px;
                background-color: #EEE;
                padding: 15px;
            }
            """))

Write templates
~~~~~~~~~~~~~~~

Now it's template-writing time.  Similar to the :ref:`simple-example`, we
create an index template:


.. testcode::

    index_template = """
    Report
    ======

    Some text.

    Samples
    -------
    $TOC
    """


We'll also create a "sample" template, that will serve as the main page for
each sample.

.. testcode::

    sample_template = """
    $title

    Overview
    --------

    This is the main page for Sample $sample.

    Detail pages
    ------------
    $TOC
    """

Next, a template for a figure page that will be under each sample.  Note that
``figure_template`` has a placeholder for an image path (``$plot_filename``).
Also, the image width has been set with the custom CSS in mind, where the CSS
will add an additional 20px of padding to the sides of the image.

Also note the internal link label ``.. _plot$number`` that has a ``$number``
placeholder to help make it unique, and the `Sphinx-style reference
<http://sphinx-doc.org/markup/inline.html#cross-referencing-arbitrary-locations>`_,
``:ref:`table$number``` that will refer to the table label (to be defined in
the next template):

.. testcode::

    figure_template = """

    .. _plot$number:

    $title

    .. figure:: $plot_filename
        :width: 500px
        :align: center

        Figure caption for sample $sample.  See :ref:`table$number` for values.
    """

Here's the table template. The ``.. cssclass::`` directive means this table
will have a border and be hover-able, as documented `here
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/examples.html#tables>`_:

.. testcode::

    table_template = """

    .. _table$number:

    $title

    Table of data for sample $number.  See :ref:`plot$number` for the figure.

    .. cssclass:: table-bordered table-hover

    $content
    """

Create content and attach pages together
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's move on to filling in the templates. First, create the index, which
doesn't need any placeholders filled in:


.. testcode::


    project.add_page(index_template, 'index.rst')


Next, we'll define a function that we'll call in the loop below.  It's standard
matplotlib to make a figure:

.. testcode::

    def make_plot(x, y, n):
        """
        Plot `x` and `y` in a scatterplot, and adding a title using `n`.

        Returns the saved filename.

        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x = np.random.random(10)
        y = np.random.random(10)
        ax.plot(x, y, 'ko')
        ax.set_title('sample %s' % n)
        fn = os.path.join(project.source_dir, '_static', 'sample%s.png' % n)
        fig.savefig(fn)
        return fn

And let's make another function to create a reST-formatted table of the data.
It uses the :func:`sphinxleash.helpers.rest_table` function, which takes a list
of rows and returns a string containing a reST-formatted table with header:

.. testcode::

    def make_table(x, y):
        contents = [('x', 'y')]
        contents.extend(zip(x, y))
        return sphinxleash.helpers.rest_table(contents, header=True)


Then can call these functions wihin a loop to generate content for each sample,
and attach the pages together:

.. testcode::

    # Five samples, each of which has a scatterplot of 10 random points and
    # a table showing the data:

    for n in range(5):

        # Add the page for the sample.
        sample_filename = 'sample%s.rst' % n
        project.add_page(
            sample_template, sample_filename,
            context=dict(title=sphinxleash.underline('Sample %s' % n), sample=n))

        # Make some random data, and plot it.
        x = np.random.random(10)
        y = np.random.random(10)
        fn = make_plot(x, y, n)

        # When filling in the template, the path needs to be relative to the
        # project's source dir, hence the relpath() call here.
        plot_filename = os.path.relpath(fn, project.source_dir)

        # Add the figure page to the sample page.  Note the `top` argument.
        project.add_page(
            figure_template,
            'figure-' + sample_filename,
            context=dict(
                title=sphinxleash.underline('Sample %s plot' % n),
                plot_filename=plot_filename,
                number=n),
            top=sample_filename,
        )

        # Add the table page to the sample page.
        project.add_page(
            table_template,
            'table-' + sample_filename,
            context=dict(
                title=sphinxleash.underline('Sample %s table' % n),
                number=n,
                content=make_table(x, y)),

            # this is used to specify the parent
            top=sample_filename
        )



Several things to things to note here:

First, the image filename handling.  In the ``savefig`` call, the image is
saved to ``advanced-example/_static/sample0.png``, but in the template, the
path needs to be relative to the source dir, or ``_static/sample0.png``.

Second, note the ``top`` kwarg to :meth:`Project.add_page`.  By default,
``top="index.rst"``, so when adding a page, ``index.rst`` will be the parent.
Here we specify the filename for the sample page to be the parent of the
details page, so in the end we get a table of contents that looks like this::

    index
        sample0
            figure-sample0
            table-sample0
        sample1
            figure-sample1
            table-sample1
        (...and so on)


Last step: render, make, and show!

.. testcode::

    project.render().make(['clean', 'html']).show()

Here's the :raw-html:`<a href="advanced-example/index.html">final product</a>`.


.. toctree::
   :maxdepth: 3

