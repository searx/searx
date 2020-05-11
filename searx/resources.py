# SPDX-License-Identifier: AGPL-3.0-or-later
"""This namespace implements *resources*:

- Working with files:

  - :py:class:`File`
  - :py:obj:`SEARX_DIR`

- Managing static files & URLs:

  - :py:func:`get_static_files`
  -  :py:class:`StaticFiles`

- Working with templates on server side and serve (static) *themes* on the
  client side:

  - :py:func:`get_templates`
  - :py:class:`Templates`
  - :py:class:`Theme`
"""

__all__ = [
    "SEARX_DIR"
    , "File"
    ,"get_static_files"
    , "StaticFiles"
    , "get_templates"
    , "Templates"
    , "Theme"
]

import sys
import os
from os import path
import platform
import io
import subprocess
from glob import iglob
import shutil
import tarfile
import zipfile

from searx import settings

if sys.version_info[0] == 2:
    # pylint: disable=redefined-builtin, undefined-variable
    str = unicode

# Global file storage
_statics = None
def get_static_files():
    """Returns the *global* manager for static files (:py:class:`StaticFiles`).  For
    initialization, application should call this function once, when preparing
    the context for the main loop and after all plugins are registered.

    :rtype: StaticFiles
    :return: Static files management object

    """
    global _statics  # pylint: disable=global-statement
    if _statics is None:
        static_path = SEARX_DIR / 'static'
        if settings['ui']['static_path'].strip():
            static_path = File(settings['ui']['static_path'].strip())
        _statics = StaticFiles(static_path)
    return _statics

class StaticFiles:
    """Manage static files which are available from client via relative URL path.

    :param File static_path:  :py:obj:`filename <File>` on filesystem

    To add :py:obj:`plugins <searx.plugins>` or :py:obj:`templates <Template>` use:

    - :py:obj:`StaticFiles.load_plugins`
    - :py:obj:`StaticFiles.load_themes`

    """

    def __init__(self, static_path):
        if not static_path.ISDIR:
            raise NotADirectoryError("static files: missing directory: %s" % static_path)
        self.path = File(static_path).ABSPATH
        """Absolute pathname of the folder used for static files."""
        self.plugins = None
        self.themes = None
        self._files = None

    def load_themes(self, themes):
        """Load :py:class:`theme's <Theme>` static files into the
        :py:obj:`StaticFiles.path`.

        """
        self.themes = themes
        for t in self.themes:
            dest_folder = self.path / t.static_url
            if t.theme_folder.REALPATH == dest_folder.REALPATH:
                # both are pointing to the same folder / nothing to do
                continue
            t.theme_folder.synctree(dest_folder)
        self._files = None # refresh file-list

    def load_plugins(self, plugins):
        """Load :py:obj:`plugin's <searx.plugins>` static files into
        :py:obj:`StaticFiles.path`.

        """
        self._files = None # refresh file-list
        self.plugins = plugins
        for plg in self.plugins:
            for fname, static_url in plugins.iter_static_files(plg):
                dest_file = self.path / static_url
                if fname.REALPATH == dest_file.REALPATH:
                    # both are pointing to the same folder / nothing to do
                    fname.syncfile(dest_file)

            for f in plg.css_dependencies + plg.js_dependencies:
                f = self.path / f
                if not f.EXISTS:
                    raise FileNotFoundError("plugin '%s': file not found: %s" % (plg.name, f))

    def files(self, refresh=False):
        """Return a set of all files found in the static path (folder and below).  The
        returned path names are relative to :py:obj:`StaticFiles.path`.

        """
        if refresh:
            self._files = None
        if self._files is None:
            self._files = set()
            for folder, _x, filenames in self.path.walk():
                rel_path = folder.relpath(self.path)
                for fname in filenames:
                    self._files.add(rel_path / fname)
        return self._files


class Theme:
    """A simple class for a theme, holding all the needed preferences (resources)."""
    # pylint: disable=too-few-public-methods

    def __init__(self, theme_name, theme_folder, static_url, template_folder):

        # e.g. a builtin 'oscar' theme ..
        self.name = theme_name
        """Theme name (:py:class:`str`)"""

        self.template_folder = template_folder.ABSPATH
        """Server's template files (:py:class:`File`)::

            /usr/local/searx/searx-src/searx/templates/<theme name>
        """

        self.result_templates = self.template_folder / 'result_templates'
        """Server's result-template files (:py:class:`File`)::

            /usr/local/searx/searx-src/searx/templates/<theme name>/result_templates
        """

        self.theme_folder = theme_folder.ABSPATH
        """Origin of theme's static files (:py:class:`File`), uploaded to client site.
        This theme folder will be synced into the :py:obj:`StaticFiles.path`.
        For builtin themes these folders are located at
        :origin:`static/themes`::

            /usr/local/searx/searx-src/searx/static/themes/<theme name>

        """

        self.favicons_folder =  theme_folder / 'img/icons'
        """Origin of theme's favicon files (:py:class:`File`).  The URL of these icons
        is inserted while rendering the HTML side.  The client loads the URLs
        (images) while loading the result page.  To be synced into the
        :py:obj:`StaticFiles.path`, the favicons must be located in a sub-folder
        of the :py:obj:`Theme.theme_folder`::

            /usr/local/searx/searx-src/searx/static/themes/<theme name>/img/icons

        """

        self.favicons = list()
        """A list of the favicons (file's basename).  This list is returned by
        :py:obj:`Templates.get_favicons` and used in the rendering context
        (``favicons``).
        """
        if self.favicons_folder.EXISTS:
            self.favicons = list(self.favicons_folder.listdir())

        # client URLs
        self.static_url = static_url
        """Relative URL (:py:class:`File`) of static files from the theme.  The base
        path of this relative URL is a URL that points to
        :py:obj:`StaticFiles.path`::

            themes/<theme name>

        """


# Global template storage
_templates = None
def get_templates():
    """Returns the *global* manager for templates and themes
    (:py:class:`Templates`).  If not not already inited, the.  For
    initialization, application should call this function once, when preparing
    the context for the main loop and after all plugins are registered.

    :rtype: Templates
    :return: Templating management object

    """
    global _templates  # pylint: disable=global-statement
    if _templates is None:
        default_theme = settings['ui']['default_theme']
        # template path
        builtin_path = SEARX_DIR / 'templates'
        if settings['ui']['templates_path'].strip():
            builtin_path = File(settings['ui']['templates_path'].strip())
        if not builtin_path.ISDIR:
            raise NotADirectoryError("templates: missing directory: %s" % builtin_path)
        _templates = Templates(builtin_path, default_theme)
    return _templates

class Templates:

    """Managing *templates* aka *themes*.  A *template* consist of a (jinja)
    template to render HTML on server site and a *theme* which delivers the
    static files needed by the client site.
    """

    def __init__(self, builtin_path, default_theme):

        self.themes = dict()
        self.default_theme = default_theme
        self.builtin_path = builtin_path

        # register builtin themes
        for theme_name in self.builtin_path.listdir():
            template_folder = self.builtin_path / theme_name
            if theme_name != '__common__' and template_folder.ISDIR:
                static_url = File('themes') / theme_name
                theme_folder = SEARX_DIR / 'static' / 'themes' / theme_name
                self.themes[theme_name] = Theme(
                    theme_name, theme_folder, static_url, template_folder
                )

    def get_result_template(self, theme_name, template_name):
        """Returns the *result* template ``template_name``.  It is used in (jinja)
        templates to include a template file conditionally.  The returned path
        of the template file is relative to `Flask.template_folder`_.

        .. _Flask.template_folder:
            https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.template_folder
        """
        theme = self.themes[theme_name]

        ret_val = File('result_templates') / template_name
        fname = theme.result_templates / template_name
        if fname.EXISTS:
            ret_val = fname.relpath(theme.template_folder.DIRNAME)

        return ret_val

    def get_favicons(self, theme_name):
        """Returns a list of favicons, its used in (jinja) templates to add favicons to
        the *results* (compare :origin:`static/themes/legacy/img/icons`)::

            {% if "icon_"~result.engine~".ico" in favicons %}
        """
        theme = self.themes[theme_name]
        return theme.favicons

class File(str):  # pylint: disable=too-many-public-methods
    """A path name to a file or folder.  Handling path names more comfortable, e.g.:

    - concatenate path names with the division operator ``/``
    - call functions like *makedirs* (aka ``mkdir -p``) directly on the path
      name
    - get properties like *EXISTS*

    .. code-block:: python

      >>> from searx.resources import File
      >>> tmp = File('~/tmp') / 'foo'
      >>> tmp
      '/home/user/tmp/foo'
      >>> tmp.EXISTS
      False

    No additional import, no juggling with ``os.join(...)``, simply slash ``/``
    and ``foo.<method>`` calls

    .. code-block:: python

      >>> [(tmp/x).makedirs() for x in ('foo', 'bar')]
      True, True
      >>> for n in tmp.listdir():
      ...     print(tmp / n)
      ...
      /home/user/tmp/foo
      /home/user/tmp/bar

    """

    class OS:
        # pylint: disable=too-few-public-methods, missing-class-docstring
        sep     = os.sep
        curdir  = os.curdir
        altsep  = os.altsep
        extsep  = os.extsep
        pathsep = os.pathsep
        defpath = os.defpath
        linesep = os.linesep
        devnull = os.devnull

    OS = OS() # pylint: disable=invalid-name

    def __new__(cls, pathname):
        """Constructor of a path name object.

        Regardless of how the encoding of the file system is, the ``pathname``
        is converted to unicode.  The conversion of byte strings is based the
        default encoding.

        To issue "File-system Encoding" See also:

        * https://docs.python.org/3/howto/unicode.html#unicode-filenames

        """
        pathname = path.normpath(path.expanduser(str(pathname)))
        return super(File, cls).__new__(cls, pathname)

    @property
    def VALUE(self):
        """string of the path name"""
        return str(self)

    @property
    def EXISTS(self):
        """True if file/pathname exist (:py:func:`os.path.exists`)"""
        return path.exists(self)

    @property
    def SIZE(self):
        """Size in bytes (:py:func:`os.path.getsize`)"""
        return path.getsize(self)

    @property
    def READABLE(self):
        """True if file/path is readable (:py:func:`os.access`)"""
        return os.access(self, os.R_OK)

    @property
    def WRITEABLE(self):
        """True if file/path is writeable (:py:func:`os.access`)"""
        return os.access(self, os.W_OK)

    @property
    def EXECUTABLE(self):
        """True if file is executable (:py:func:`os.access`)"""
        return os.access(self, os.X_OK)

    @property
    def ISDIR(self):
        """True if path is a folder (:py:func:`os.path.isdir`)"""
        return path.isdir(self)

    @property
    def ISFILE(self):
        """True if path is a file (:py:func:`os.path.isfile`)"""
        return path.isfile(self)

    @property
    def ISABSPATH(self):
        """True if path is absolute (:py:func:`os.path.isabs`)"""
        return path.isabs(self)

    @property
    def ISLINK(self):
        """True if path is a symbolic link (:py:func:`os.path.islink`)"""
        return path.islink(self)

    @property
    def ISMOUNT(self):
        """True if path is a mountpoint (:py:func:`os.path.ismount`)"""
        return path.ismount(self)

    @property
    def MTIME(self):
        """Return the last modification time, reported by :py:func:`os.stat`."""
        return os.stat(self).st_mtime

    @property
    def ATIME(self):
        """Return the last access time, reported by :py:func:`os.stat`."""
        return os.stat(self).st_atime

    @property
    def CTIME(self):
        """Return the metadata change time, reported by :py:func:`os.stat`."""
        return os.stat(self).st_ctime

    @property
    def ISZIP(self):
        """True if path is a ZIP file (:py:func:`zipfile.is_zipfile`)"""
        return zipfile.is_zipfile(self)

    @property
    def ISTAR(self):
        """True if path is a TAR archive file (:py:func:`tarfile.is_tarfile`)"""
        return tarfile.is_tarfile(self)

    @property
    def DIRNAME(self):
        """The path name of the folder, where the file is located
        (:py:func:`os.path.dirname`).

        E.g.: ``/path/to/folder/filename.ext`` --> ``/path/to/folder``

        """
        return self.__class__(path.dirname(self))

    @property
    def BASENAME(self):
        """The path name with suffix, but without the folder name
        (:py:func:`os.path.basename`).

        E.g.: ``/path/to/folder/filename.ext`` --> ``filename.ext``

        """
        return self.__class__(path.basename(self))

    @property
    def FILENAME(self):
        """The path name without folder and suffix.

        E.g.: ``/path/to/folder/filename.ext`` --> ``filename``

        """
        return self.__class__(path.splitext(path.basename(self))[0])

    @property
    def SUFFIX(self):
        """The filename suffix (last part of :py:func:`os.path.splitext`)

        E.g.: ``/path/to/folder/filename.ext`` --> ``.ext``

        """
        return self.__class__(path.splitext(self)[1])

    @property
    def SKIPSUFFIX(self):
        """The complete file name without suffix (first part of
        :py:func:`os.path.splitext`).

        E.g.: ``/path/to/folder/filename.ext`` --> ``/path/to/folder/filename``

        """
        return self.__class__(path.splitext(self)[0])

    @property
    def ABSPATH(self):
        """The absolute pathname (:py:func:`os.path.abspath`)

        E.g: ``../to/../to/folder/filename.ext`` --> ``/path/to/folder/filename.ext``

        """
        return self.__class__(path.abspath(self))

    @property
    def REALPATH(self):
        """The real pathname without symbolic links (:py:func:`os.path.realpath`)."""
        return self.__class__(path.realpath(self))

    @property
    def POSIXPATH(self):
        """The path name in *POSIX* notation.

        Help full if you are on MS-Windows and need the POSIX name.
        """
        if os.sep == "/":
            return str(self)

        p = str(self)
        if p[1] == ":":
            p = "/" + p.replace(":", "", 1)
        return p.replace(os.sep, "/")

    @property
    def NTPATH(self):
        """The path name in the Windows (NT) notation.
        """
        ret_val = None
        if os.sep == "\\":
            ret_val = str(self)
        else:
            ret_val = str(self).replace(os.sep, "\\")
        return ret_val

    @property
    def EXPANDVARS(self):
        """Path with environment variables expanded (:py:func:`os.path.expandvars`)."""
        return self.__class__(path.expandvars(self))

    @property
    def EXPANDUSER(self):
        """Path with an initial component of ~ or ~user replaced by that user's home
        (:py:func:`os.path.expanduser`)."""
        return self.__class__(path.expanduser(self))

    @classmethod
    def getHOME(cls):
        """User's home folder."""
        return cls(path.expanduser("~"))

    @classmethod
    def getCWD(cls):
        """Current working directory (:py:func:`os.getcwd`)."""
        return cls(os.getcwd())

    def chdir(self):
        """change the current working directory to *self* (:py:func:`os.chdir`)."""
        os.chdir(self)

    def makedirs(self, mode=0o775):
        """Recursive directory creation, default mode is 0o775 [octal]. Uses
        :py:func:`os.path.os.makedirs` but prevent exception if folder exists.

        :param int mode: file permissions
        :return: created (True) already exists (True),
        :raises Exception: in case of errors (permissions, etc.)

        """
        ret_val = False
        if not self.ISDIR:
            os.makedirs(self, mode)
            ret_val = True
        return ret_val

    def __div__(self, pathname):
        """Concatenate path names with ``/``"""
        return self.__class__(self.VALUE + os.sep + str(pathname))
    __truediv__ = __div__

    def __rdiv__(self, pathname):
        """Concatenate path names with ``/``"""
        return self.__class__(str(pathname) + os.sep + self.VALUE)

    def __add__(self, other):
        """Add string to the path name with ``+``"""
        return self.__class__(self.VALUE + str(other))

    def __radd__(self, other):
        """Add string to the path name with ``+``"""
        return self.__class__(str(other) + self.VALUE)

    def relpath(self, start):
        """Return a relative version of a path (:py:func:`os.path.relpath`)"""
        return self.__class__(path.relpath(self, start))

    def splitpath(self):
        """Split a pathname.  Return tuple (head, tail) where tail is everything after
        the final slash (:py:func:`os.path.split`).
        """
        head, tail = path.split(self)
        return (self.__class__(head), self.__class__(tail))

    def listdir(self):
        """Return a iterator which yields the names of the files in the directory
        (:py:func:`os.listdir`)."""
        for name in os.listdir(self):
            yield self.__class__(name)

    def glob(self, pattern, relpath=False):
        """Return an iterator which yields the paths matching a pathname pattern.  The
        pattern may contain simple shell-style wildcards a la fnmatch. However,
        unlike fnmatch, filenames starting with a dot are special cases that are
        not matched by '*' and '?'  patterns.

        """
        for name in  iglob(self / pattern):
            obj = self.__class__(name)
            if relpath is True:
                obj = obj.relpath(self)
            yield obj

    def walk(self, topdown=True, onerror=None, followlinks=False):
        """Directory tree generator.  For each directory in the directory tree
        rooted at top (including top itself, but excluding '.' and '..'), yields
        a 3-tuple::

            folder, dirnames, filenames

        dirnames is a list of the names of the subdirectories in dirpath
        (excluding '.' and '..').  filenames is a list of the names of the
        non-directory files in dirpath.

        Note that the names in the lists are just names, with no path components.
        To get a full path (which begins with top) to a file or directory in
        dirpath, do ``folder / name``.

        By default, os.walk does not follow symbolic links to subdirectories on
        systems that support them.  In order to get this functionality, set the
        optional argument 'followlinks' to true.

        .. caution::

           If you pass a relative pathname for top, don't change the current
           working directory between resumptions of walk.  ``walk`` never
           changes the current directory and assumes that the client doesn't
           either.

        For more details see ``os.walk``

        """

        # argh those fu.. idiots from python implemented fspath in 3.4 which no
        # longer supports string-like objects (inheritance of str) in os.walk.
        # So we have to typecast str(self).

        for dirpath, dirnames, filenames in os.walk(str(self), topdown, onerror, followlinks):
            dirs = [self.__class__(x) for x in dirnames]

            yield (self.__class__(dirpath)
                   , dirs
                   , [self.__class__(x) for x in filenames])

            for name in list(dirnames):
                if name not in dirs:
                    dirnames.remove(name)

    def suffix(self, new_suffix):
        """Return path name with ``new_suffix``"""
        return self.__class__(self.SKIPSUFFIX + new_suffix)

    def copyfile(self, dest, preserve=False):
        """Copy the file src to the file or directory dest (:py:func:`shutil.copy`
        and :py:func:`shutil.copy2`).

        :dest str: The destination may be a directory
        :preserve bool: copies permission bits

        """
        if preserve:
            shutil.copy2(self, dest)
        else:
            shutil.copy(self, dest)

    def copytree(self, dest, symlinks=False, ignore=None):
        """Recursively copy the entire directory tree (:py:func:`shutil.copytree`)"""
        shutil.copytree(self, dest, symlinks, ignore)

    def synctree(self, dest):
        """Recursive sync all files and folders into ``dest`` folder.  If ``dest``
        folder does not exists, it is created.  Symbolic links in the ``source``
        (self) will be traversed and all files and folders will be synced into
        ``dest`` folder just by copying (symlinks will be plain files in the
        destination).  The function returns a list with all synced files in.
        """
        ret_val = []
        _force_all = False
        if not (self.EXISTS and self.ISDIR):
            raise NotADirectoryError("synctree: source %s" % self)
        if self.REALPATH == dest.REALPATH:
            # both are pointing to the same folder / nothing to do
            return ret_val
        if not dest.EXISTS:
            _force_all = True
            dest.makedirs()
        for folder, _x, filenames in self.walk():
            dst_folder = (dest / folder.relpath(self))
            _force_folder = False
            if _force_all or not dst_folder.EXISTS:
                dst_folder.makedirs()
                _force_folder = True
            for fname in filenames:
                src = folder / fname
                dst = dst_folder / fname
                if src.syncfile(dest, force=(_force_all or _force_folder)):
                    ret_val.append(dst)
        return ret_val

    def syncfile(self, dst, force=False):
        """Sync file.  Copy file to destination ``dst`` if *self* is newer.  The
        function returns ``True`` when file was synced otherwise, if file was
        not synced, ``False`` is returned.
        """
        ret_val = False
        if force or not dst.EXISTS or self.MTIME > dst.MTIME :
            ret_val = True
            with open(self, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    while 1:
                        buf = fsrc.read(128*1024)
                        if not buf:
                            break
                        fdst.write(buf)
        return ret_val

    def move(self, dest):
        """Move path to ``dest`` location (:py:func:`shutil.move`)"""
        shutil.move(self, dest)
        return self.__class__(dest)

    def delete(self):
        """remove file/folder, uses :py:func:`shutil.rmtree` and
        :py:func:`os.remove`."""
        if self.ISDIR:
            self.rmtree()
        else:
            self.rmfile()

    def rmtree(self, ignore_errors=False, onerror=None):
        """remove tree, arguments see :py:func:`shutil.rmtree`"""
        shutil.rmtree(self, ignore_errors, onerror)

    def rmfile(self):
        """remove file using :py:func:`os.remove`"""
        os.remove(self)

    def filesize(self, precision=None):
        """Filesize in bytes or with precision"""
        size = path.getsize(self)
        if precision is not None:
            size = humanize_bytes(size, precision)
        return size

    def open_text_file(self
                       , mode='rt', encoding='utf-8'
                       , errors='strict', buffering=1
                       , newline=None):
        """Open file as text file.

        wraps `io.open <https://docs.python.org/library/io.html#io.open>`_:

        * except argument ``closefd`` (meaningless when using filenames)
        * ``encoding='utf-8'`` is default
        * ``mode='rt'`` is default
        * ``buffering=1`` is default (selects line buffering)
        """
        return io.open(self
                       , mode=mode, encoding=encoding
                       , errors=errors, buffering=buffering
                       , newline=newline)

    def open_binary_file(self, mode='rb', errors='strict', buffering=None):
        """Open file as binary file.

        wraps `io.open <https://docs.python.org/library/io.html#io.open>`_:

        * except argument ``closefd`` (meaningless when using filenames)
        * except argument ``encoding`` (meaningless since *binary*)
        * except argument ``newline`` (meaningless since *binary*)
        * ``mode='rb'`` is default
        """
        return io.open(self, mode=mode, errors=errors, buffering=buffering)

    def start_file(self):
        """Start a file with its associated application."""
        system  = platform.system()
        if system == 'Windows':
            os.startfile(self) # pylint: disable=no-member
            return
        cmd = 'xdg-open'
        if system in ('FreeBSD', 'Darwin'):
            cmd = 'open'

        cmd = self.which(cmd, findall=False)
        if cmd:
            os.system(cmd + " " + self)

    def read_file(self, encoding='utf-8', errors='strict'):
        """read entire file"""
        with self.open_text_file(encoding=encoding, errors=errors) as f:
            return f.read()

    def Popen(self, *args, **kwargs):  # pylint: disable=invalid-name
        """Get a :py:class:`subprocess.Popen` object (``proc``).

        The path name of the self-object is the program to call.  The program
        arguments are given py ``*args`` and the ``*kwargs`` are passed to the
        :py:class:`subprocess.Popen` constructor. The ``universal_newlines`` is
        true by default (see `Python library / Popen constructor`_).

        .. code-block:: python

           proc = File("arp").Popen("-a",)
           stdout, stderr = proc.communicate()
           ret_val = proc.returncode
           print("stdout: %s" % stdout)
           print("stderr: %s" % stderr)
           print("exit code = %d" % ret_val)

        .. _Python library / Popen constructor:
           https://docs.python.org/3/library/subprocess.html#popen-constructor
        """

        defaults = {
            'stdout'             : subprocess.PIPE,
            'stderr'             : subprocess.PIPE,
            'stdin'              : subprocess.PIPE,
            'universal_newlines' : True,
        }
        defaults.update(kwargs)
        return subprocess.Popen([self,] + list(args), **defaults)

    @classmethod
    def which(cls, cmd, findall=False):
        """Searches the ``cmd`` in the ``PATH`` enviroment.

        This *which* is not POSIX conform.  On Win it searches the ``cmd`` (given
        without extension) in %%PATH%% by adding extensions from %%PATHEXT%%.
        On POSIX it searches for ``cmd`` which is executable.

        If nothing is found, ``None`` is returned, otherwise the path name of
        the executable is returned.  With option ``findall=True`` all matches
        are returned in a list.

        """
        envpath = OS_ENV.get('PATH') or os.defpath
        hits = list()
        cmd  = File(cmd)

        if sys.platform == 'win32':
            exe = [x.lower() for x in os.environ.get("PATHEXT", [""]).split(";")]
            for folder in envpath.split(os.pathsep):
                for ext in exe:
                    fullname = File(folder) / cmd + ext
                    if fullname.ISFILE:
                        if not findall:
                            return fullname
                        hits.append(fullname)
        else:
            for folder in envpath.split(os.pathsep):
                fullname = File(folder) / cmd
                if fullname.EXECUTABLE:
                    if not findall:
                        return fullname
                    hits.append(fullname)
        return hits or None

SEARX_DIR = File(__file__).DIRNAME
"""Folder where searx *software* is installed.  Builtin resources are shipped in
sub-folders like ``./static`` for the client side or e.g. ``./templates`` for
the server.
"""

def humanize_bytes(size, precision=2):
    """Determine the *human readable* value of bytes on 1024 base (1KB=1024B).

    """
    s = ['B ', 'KB', 'MB', 'GB', 'TB']
    x = len(s)
    p = 0
    while size > 1024 and p < x:
        p += 1
        size = size/1024.0
    return "%.*f %s" % (precision, size, s[p])

class OS_ENV(dict): # pylint:disable=invalid-name

    """Environment object to access :py:class:`os.environ` by object's attribute
    names.

    .. code-block:: python

       >>> if OS_ENV.get("SHELL") is None:
               OS_ENV.SHELL = "/bin/bash"
       >>> OS_ENV.SHELL
       '/bin/bash'

    """
    @property
    def __dict__(self):
        return os.environ

    def __getattr__(self, attr):
        return os.environ[attr]

    def __setattr__(self, attr, val):
        os.environ[attr] = val

    def get(self, attr, default=None):
        return os.environ.get(attr, default)

OS_ENV = OS_ENV()
