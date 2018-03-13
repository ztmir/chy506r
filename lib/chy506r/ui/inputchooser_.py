# -*- coding: utf8 -*-
"""Defines InputChooser class
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import glob
import os
import pathlib

from . import images_

__all__ = ('InputChooser',)


class InputChooser(tk.Frame):
    def __init__(self, master, **kw):

        super().__init__(master)

        self._selection = ''
        self._create_widgets()
        self._updatecommand = kw.get('updatecommand', lambda: True )

    @property
    def label(self):
        return self._label

    @property
    def combobox(self):
        return self._combobox

    @property
    def selection(self):
        return self._selection

    def _create_widgets(self):
        image = tk.PhotoImage(data=self._image_data())
        self._label = tk.Label(self, image=image, width='16m')
        self._label.image = image  # Keep a reference!
        self._combobox = ttk.Combobox(self, **self._combo_options())
        # layout
        self.label.pack(side=tk.LEFT, fill=tk.BOTH, padx=2, pady=4)
        self.combobox.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2, pady=4)

    def _combo_options(self):
        validate = self.register(self._validate)
        invalid = self.register(self._invalid)
        return {'postcommand': self._generate_values,
                'validate': 'focus',
                'validatecommand': (validate, '%V', '%P'),
                'invalidcommand': (invalid, '%P')}

    def _validate(self, reason, value):
        if value :
            if not pathlib.Path(value).is_char_device():
                messagebox.showerror("Invalid path", ("%s is not a character" +
                                     " device") % repr(value))
                return False
            with open(value, 'r') as fr, open(value, 'w') as fw:
                if not fr.isatty() or not fw.isatty():
                    messagebox.showerror("Invalid path", "%s is not a TTY"
                                         % repr(value))
                    return False

        self._selection = self.combobox.get()
        self._updatecommand()
        return True

    def _invalid(self, value):
        self.combobox.set(self.selection)

    def _generate_values(self):
        serials = glob.glob('/dev/serial/by-id/*')
        values = [os.path.realpath(f) for f in serials]
        self.combobox['values'] = values

    @classmethod
    def _image_data(cls):
        return images_.input_file

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
