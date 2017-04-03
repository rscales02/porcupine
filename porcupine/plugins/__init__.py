"""Plugin system for Porcupine.

Porcupine comes with many handy plugins, and you can read them to
get an idea of how everything works. You can find them like this:

    >>> import porcupine.plugins
    >>> porcupine.plugins.__path__
    ['/bla/bla/bla/porcupine/plugins',
     '/home/akuli/.config/porcupine/plugins']
    >>>

Porcupine's built-in plugins are installed in the first directory and
you can add your own plugins to the second directory.

Plugins are just Python files that Porcupine imports on startup, so
their names need to be valid module names. The files should import
porcupine and call porcupine.plugins.add_plugin(). You can read the
built-in plugins for examples.

When you have added a plugin file, run Porcupine from a terminal,
command prompt or PowerShell so you'll see any errors messages that your
plugin might produce. Note that you don't need to save all files you
have opened in Porcupine; there's nothing wrong with running multiple
Porcupines at the same time.
"""

import importlib
import logging
import os
import types

import porcupine


# simple hack to allow user-wide plugins
__path__.append(porcupine.dirs.userplugindir)

# __path__ will show up in help() too because the module docstring
# recommends checking it out
__all__ = ['add_plugin', '__path__']

log = logging.getLogger(__name__)
plugins = []


def _do_nothing(*args):
    pass


def add_plugin(name, *, start_callback=_do_nothing, filetab_hook=_do_nothing,
               setting_widget_factory=_do_nothing):
    """Add a new plugin to Porcupine when it's starting.

    The name argument can be any string that does not conflict with
    other plugins. These are the valid keyword arguments to this
    function, and they all do nothing by default:

      start_callback(editor)
        This function will be called with a porcupine.editor.Editor
        object as its only argument when Porcupine starts.

      filetab_hook(filetab)
        This function is called when a new filetabs.FileTab is created.
        It should set up the filetab, and then optionally yield and undo
        everything it did. It will be called with a
        porcupine.filetabs.FileTab object as the only argument.

      setting_widget_factory(labelframe):
        This function is called when the setting dialog is opened for
        the first time. It should create other tkinter widgets for
        changing the settings into the given tkinter LabelFrame widget.
        The labelframe is displayed in the setting dialog only if this
        callback returns True.
    """
    plugin = types.SimpleNamespace(
        name=name,
        start_callback=start_callback,
        filetab_hook=filetab_hook,
        setting_widget_factory=setting_widget_factory,
    )
    plugins.append(plugin)


# these are wrapped tightly in try/except because someone might write
# Porcupine plugins using Porcupine, so Porcupine MUST be able to start
# if the plugins are broken

def load(editor):
    assert not plugins, "cannot load plugins twice"

    modulenames = set()
    for path in __path__:    # this line looks odd
        for name, ext in map(os.path.splitext, os.listdir(path)):
            if name.isidentifier() and name[0] != '_' and ext == '.py':
                modulenames.add(__name__ + '.' + name)

    for name in modulenames:
        try:
            importlib.import_module(name)
        except Exception:
            log.exception("problem with importing %s", name)
        else:
            log.debug("successfully imported %s", name)

    log.info("found %d plugins", len(plugins))
    for plugin in plugins:
        try:
            plugin.start_callback(editor)
        except Exception as e:
            log.exception("the %r plugin's start_callback doesn't work",
                          plugin.name)


# the filetab stuff looks like a context manager at this point, but
# filetabs.py is actually simpler when these are kept apart like this

# TODO: would it be better to just expose some minimal callback based
# plugin API in filetabs.py and other places?

def init_filetab(filetab):
    state = []      # [(plugin, generator), ...]
    for plugin in plugins:
        try:
            generator = plugin.filetab_hook(filetab)
            if generator is None:
                # no yields
                continue
            next(generator)
            state.append((plugin.name, generator))

        except Exception:
            log.exception("the %r plugin's filetab_hook doesn't work",
                          plugin.name)

    filetab.__plugin_state = state


def destroy_filetab(filetab):
    for name, generator in filetab.__plugin_state:
        try:
            next(generator)
        except StopIteration:
            # it didn't yield, let's assume there's nothing to clean up
            pass
        except Exception:
            log.exception("the %r plugin's filetab_hook doesn't work", name)