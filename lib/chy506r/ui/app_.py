# -*- coding: utf8 -*-
"""
"""

import tkinter as tk

from .inputchooser_ import *
from .outputchooser_ import *
from .controller_ import *

__all__ = ('App',)

class _AppMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls._tk = None
        cls._ui = None

    @property
    def tk(cls):
        if cls._tk is None:
            cls._tk = tk.Tk()
        return cls._tk

    @property
    def ui(cls):
        if cls._ui is None:
            cls._ui = cls(cls.tk)
        return cls._ui


class App(tk.Frame, metaclass=_AppMeta):
    """Application main frame"""

    def __init__(self, master):
        """Initialize the application main frame"""

        super().__init__(master)

        self._configure_master()
        self._create_components()
        self.pack()
        self.update_widgets()

    @property
    def input_chooser(self):
        return self._input_chooser

    @property
    def output_chooser(self):
        return self._output_chooser

    @property
    def controller(self):
        return self._controller

    def _configure_master(self):
        self.master.title("CHY 506R")
        self.master.protocol("WM_DELETE_WINDOW", self._wm_delete_window)

    def _wm_delete_window(self):
        """Callback invoked in response to WM_DELETE_WINDOW protocol"""
        self.controller.stop()
        self.master.destroy()

    def update_widgets(self):
        self.controller.update_widgets()
        self._update_status_bar()

    def _create_components(self):
        self._input_chooser = InputChooser(self, updatecommand=self.update_widgets)
        self._output_chooser = OutputChooser(self, updatecommand=self.update_widgets)
        self._controller = Controller(self, updatecommand=self.update_widgets, input_chooser=self.input_chooser, output_chooser=self.output_chooser)
        self._status_bar = tk.Label(self, text="Idle", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        # layout
        self.input_chooser.pack(expand=True, fill=tk.BOTH)
        self.output_chooser.pack(expand=True, fill=tk.BOTH)
        self.controller.pack(expand=True, fill=tk.BOTH)
        self._status_bar.pack(expand=True, fill=tk.BOTH)

    def _update_status_bar(self):
        if self.controller.device_running():
            text = "Measurements in progress (%d samples collected)..." % \
                   self.controller.device.count
        else:
            text = "Idle"
        self._status_bar['text'] = text


# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
