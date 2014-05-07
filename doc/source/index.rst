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
2. Write reST templates (plain strings) for each page
3. Connect the pages together
4. Render and view

Below is the code to create two projects: a simple one with mostly default
settings and minimal text, just to give an idea of the workflow, and a second,
more complex one with customization (Bootstrap theme, custom CSS, custom Sphinx
extensions) and more content (images, reports).

Here are the end products:

* :raw-html:`<a href="simple-example/index.html">Simple example</a>`
* :raw-html:`<a href="advanced-example/index.html">Advanced example</a>`

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


Create a new project
~~~~~~~~~~~~~~~~~~~~
First, let's configure and initialize a project:

.. testcode::

    import sphinxleash

    # Configure a project.  We'll use the defaults for this example; the
    # directory will be created if needed.
    project = sphinxleash.Project(dirname='simple-example')


    # Initialize the project.  This calls sphinx-quickstart and creates some
    # files to populate the documentation.  Use `silent=False` to get more info
    # on what it's doing.
    project.create_new()

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
Now we use the :meth:`Project.add_page` method to populate the project with reST
templates, filling in the templates with different `context` dictionaries.

The :file:`index.rst` page is special for Sphinx, and always has to exist.  So
it's a good idea to make it first.  It doesn't have any custom placeholders, so
all we have to do is specify the template and the filename.  The `project`
object will figure out the source directory of the project, and save
:file:`index.rst` in the right place:

.. testcode::

    # First the top-level index page
    project.add_page(index_template, 'index.rst')

Let's make some more pages.  For each page, we're making a new `context`
dictionary which will be used to fill in the placeholders for the
`page_template`.

.. testcode::

    for n in range(10):

        # Helper function for making reST titles with underlines
        title = sphinxleash.underline('Sample %s' % n, symbol="=")

        # This dict will be used to fill in placeholders
        context = dict(title=title, number=n)

        filename = 'page%s.rst' % n

        project.add_page(page_template, filename, context)





Render and view
~~~~~~~~~~~~~~~
At this point, no files have actually been created on disk yet.  We've simply
told :mod:`sphinxleash` how to connect pages together and how to fill in their
content.  To actually do this, we need to call the :meth:`Project.render`
method:

.. testcode::

    # Writes the configured .rst files to the project directory
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

Advanced example
----------------
This is a considerably more advanced example.  To replicate it, you'll need to
have `matplotlib <http://matplotlib.org/>`_ (for figure-making) and
`sphinx_bootstrap_theme
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html>`_ installed.
This example includes:

- using the ``sphinx_bootstrap_theme`` and setting theme options in the
  :file:`conf.py` file generated by Sphinx
- customizing the Jinja HTML layout template
- adding custom CSS styles
- plotting figures for each sample and including them in each sample page
- nesting pages

First, make sure you can import these:

.. testcode::

    import sphinxleash
    import sphinx_bootstrap_theme
    from matplotlib import pyplot as plt
    import numpy as np


As in the :ref:`simple-example`, we configure a new :class:`Project`.  The
``config_dict`` argument is used to override variables in the :file:`conf.py`
file generated by Sphinx.  ere, we make some changes as documented in the
`sphinx_bootstrap_theme docs
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html#customization>`_
for using the Bootstrap theme.

We can also specify additional arguments to ``sphinx-quickstart`` using the
``quickstart_params`` argument.  Here, we're just setting the author name.
Other options can be found by inspecting the
:attr:`sphinxleash.quickstart_defaults` dictionary.

As before, at the end we call :meth:`Project.create_new` to actually create the
files.  This method also does the in-place modification of :file:`conf.py`
after it's initially created.

.. testcode::

    project = sphinxleash.Project(
        "advanced-example",
        conf_dict=dict(
            html_theme='bootstrap',
            html_theme_path=sphinx_bootstrap_theme.get_html_theme_path(),
            html_theme_options=dict(
                navbar_title='sphinxleash advanced example',
                bootswatch_theme='flatly'
            ),
            html_static_path=['_static'],
            templates_path=['_templates'],
        ),
        # Only make a small change in the quickstart config
        quickstart_params=dict(author='sphinxleash-created'),
    )
    project.create_new()

Now we're going to make some changes to the layout, as documented `here
<http://ryan-roemer.github.io/sphinx-bootstrap-theme/README.html#extending-layout-html>`_.
We use :attr:`project.source_dir` to get the source directory correct:

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
This makes the footer text red (to make a visibly obvious change) and also
makes some tweaks to how figures and figure captions will be displayed. Note
that the path for this CSS file, relative to :file:`layout.html`, needs to
match what we set for the `bootswatch_css_custom` line in :file:`layout.html`
above.

.. testcode::

    with open(os.path.join(project.source_dir, '_static', 'style.css'), 'w') as fout:
        fout.write(dedent(
            """
            footer {
                color: red;
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

Now it's template-writing time.  Similar to the :ref:`simple-example`, we
create an index template and a page template.  We'll also create a "sub-page"
template, which will be nested below each sample and can be used for sample
details.

Note that the sample template has a placeholder for an image path
(``$plot_filename``).  Also, the image width has been set with the custom CSS
in mind, which will add 20px of padding.

.. testcode::

    index_template = """
    Report
    ======

    Some text.

    Samples
    -------
    $TOC
    """

    sample_template = """
    $title

    Info about Sample $sample.

    .. figure:: $plot_filename
        :width: 500px
        :align: center

        Figure caption for sample $sample.

    Detail pages
    ------------
    $TOC
    """

    subpage_template = """
    $title
    More details for sample $number can be found here.
    """

Let's move on to filling in the templates:


.. testcode::


    # First create the index, which doesn't need any placeholders filled in.
    project.add_page(index_template, 'index.rst')


    # Five samples, each of which has a scatterplot of 10 random points:

    for n in range(5):

        # Create the figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(np.random.random(10), np.random.random(10), 'k.')
        ax.set_title('sample %s' % n)

        # The actual figure is saved here...
        fn = os.path.join(project.source_dir, '_static', 'sample%s.png' % n)
        fig.savefig(fn)

        # ...but when filling in the template, the path needs to be relative to
        # the project's source dir, hence the relpath() call here.
        plot_filename = os.path.relpath(fn, project.source_dir)

        # Fill in the context dictionary...
        title = sphinxleash.underline('Sample %s' % n)
        context = dict(title=title, plot_filename=plot_filename, sample=n)
        filename = 'sample%s.rst' % n

        # ...and add the page.
        project.add_page(sample_template, filename, context=context)

        subpage_context = dict(
            title=sphinxleash.underline('Sample %s details' % n),
            number=n
        )
        project.add_page(
            subpage_template,
            'details-' + filename,
            subpage_context,

            # this is used to specify the parent
            top=filename
        )

Two things to note here:

First, the image filename handling.  In the ``savefig`` call, the image is
saved to ``advanced-example/_static/sample0.png``, but in the template, the
path needs to be relative to the source dir, or ``_static/sample0.png``.

Second, note the ``top`` kwarg to :meth:`Project.add_page`.  By default,
``top="index.rst"``, so when adding a page, ``index.rst`` will be the parent.
Here we specify the filename for the sample page to be the parent of the
details page, so in the end we get a table of contents that looks like this::

    index
        sample0
            details-sample0
        sample1
            details-sample1
        (...and so on)


Last step: render, make, and show!

.. testcode::

    project.render().make(['clean', 'html']).show()

Here's the :raw-html:`<a href="advanced-example/index.html">final product</a>`.


.. toctree::
   :maxdepth: 3

