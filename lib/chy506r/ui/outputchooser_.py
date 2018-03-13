# -*- coding: utf8 -*-
"""Defines OutputChooser class
"""

import tkinter as tk
import tkinter.filedialog as filedialog

from . import images_

__all__ = ('OutputChooser',)


class OutputChooser(tk.Frame):
    def __init__(self, master, **kw):

        super().__init__(master)

        self._create_widgets()
        self._selection = ''
        self._updatecommand = kw.get('updatecommand', lambda: True )
        self._override = False

    @property
    def button(self):
        return self._button

    @property
    def label(self):
        return self._label

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        self._selection = value
        self._label['text'] = value or 'No file selected'
        self._updatecommand()

    @property
    def override(self):
        return self._override

    @override.setter
    def override(self, value):
        self._override = value

    def select(self):
        types = [('Comma Separated Values', '*.csv'), ('All files', '*')]
        config = {'master': self.master, 'defaultextension': '.csv', 'filetypes': types}
        if self._selection:
            config['initialfile'] = self._selection

        answer = filedialog.asksaveasfilename(**config)

        if answer and isinstance(answer, str):
            self.selection = answer
            self.override = True
        return answer

    def _create_widgets(self):
        image = tk.PhotoImage(data=self._image_data())
        self._button = tk.Button(self, image=image, width='16m', command=self.select)
        self._button.image = image  # Keep a reference!
        self._label = tk.Label(self, borderwidth=1, relief=tk.RIDGE, text='No file selected')
        # layout
        self.button.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.BOTH)
        self.label.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.X, expand=True)

    @classmethod
    def _image_data(cls):
        return images_.output_file



# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
