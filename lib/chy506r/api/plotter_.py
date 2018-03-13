# -*- coding: utf8 -*-

import subprocess
import tempfile
import os

__all__ = ('Plotter', )


class Plotter(object):
    """Plots temperature graph in a separate window.

    Current implementation uses gnuplot run via subprocess.Popen."""

    def __init__(self, data_file, gnuplot='gnuplot', **kw):
        self._subprocess = None
        self.data_file = data_file
        self.gnuplot = gnuplot
        self._scriptfd, self._script_file = self._write_script(**kw)

    @property
    def script_file(self):
        """Path to gnuplot script file"""
        return self._script_file

    @property
    def subprocess(self):
        """Subprocess running gnuplot executable"""
        return self._subprocess

    def running(self):
        """Returns True if the gnuplot subprocess is already running"""
        return self.subprocess is not None and self.poll() is None

    def cmd(self):
        """Returns full commandline for running gnuplot through Popen"""
        return [self.gnuplot, '-e', "file='%s'" % self.data_file,
                self.script_file]

    def start(self, **kw):
        """Starts plotter subprocess (gnuplot)"""
        self._subprocess = subprocess.Popen(self.cmd(), **kw)

    def poll(self):
        """Check if child gnuplot process has terminated. Set and return
        returncode attribute. Otherwise returns None"""
        return self.subprocess.poll()

    def terminate(self):
        """Terminates gnuplot subprocess"""
        self.subprocess.terminate()

    @classmethod
    def _write_script(cls, **kw):
        """Write gnuplot script to a temporary file for further use.

        Returns a tuple of file descriptor and name of the created file."""
        (fd, name) = tempfile.mkstemp()
        fd = os.fdopen(fd, 'wt')
        fd.write(cls._script(**kw))
        fd.flush()
        return (fd, name)

    @classmethod
    def _script(cls, **kw):
        """Returns a gnuplot script as string"""
        options = dict({
            'yrange': '[0:300]',
            'title': 'Temperatures'
        }, **kw)

        return """
        # Bindings
        bind "Close" "reread_loop = 0"
        reread_loop = 1

        # Plot Title
        set title "%(title)s"

        # X axis settings
        set xdata time
        set timefmt "%%H:%%M:%%S"
        set format x "%%H:%%M:%%S"
        set xtics rotate by 45 right

        # Y axis
        set yrange %(yrange)s

        # Grid
        set grid

        # draw chart from a file
        set datafile separator ';'
        plot file using "TIME":"T1" with lines title "T1", \
             file using "TIME":"T2" with lines title "T2"
        pause 1
        if(reread_loop==1) reread

        """ % options



# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
