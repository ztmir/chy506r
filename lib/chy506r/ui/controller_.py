# -*- coding: utf8 -*-
"""Defines Controller class
"""

import tkinter as tk
import tkinter.messagebox as messagebox
import os

from . import images_
from .. import api

__all__ = ('Controller',)


class Controller(tk.Frame):
    """A frame with control buttons"""

    def __init__(self, master, **kw):
        """Initializes the Controller"""
        super().__init__(master)

        self._device = None
        self._plotter = None
        self._updatecommand = kw.get('updatecommand', lambda: True)
        self._input_chooser = kw.get('input_chooser', master.input_chooser)
        self._output_chooser = kw.get('output_chooser', master.output_chooser)
        self._create_widgets()
        self._image.index = 1

    @property
    def image(self):
        return self._image

    @property
    def start_button(self):
        return self._start_button

    @property
    def stop_button(self):
        return self._stop_button

    @property
    def plot_button(self):
        return self._plot_button

    @property
    def tty(self):
        return self.input_chooser.selection

    @property
    def output(self):
        return self.output_chooser.selection

    @property
    def device(self):
        return self._device

    @property
    def plotter(self):
        return self._plotter

    @property
    def input_chooser(self):
        return self._input_chooser

    @property
    def output_chooser(self):
        return self._output_chooser

    def device_running(self):
        return self._device is not None and self._device.is_alive()

    def plotter_running(self):
        return self._plotter is not None and self._plotter.running()

    def update_widgets(self):
        """Updates buttons state (disabled/enabled) to resemble application state"""
        device_running = self.device_running()
        start = not device_running and self.tty and self.output
        stop = device_running
        plot = not self.plotter_running() and (device_running and self._device.count >= 2)
        self._start_button['state'] = tk.NORMAL if start else tk.DISABLED
        self._stop_button['state'] = tk.NORMAL if stop else tk.DISABLED
        self._plot_button['state'] = tk.NORMAL if plot else tk.DISABLED
        self._update_image()

    def stop(self):
        self._stop_device()
        self._stop_plotter()

    def _update_image(self):
        if self.device_running():
            self.image.configure(image=self._image_frames[self._image_index])
            self._image_index += 1
            if self._image_index == 30:
                self._image_index = 0

    def _create_widgets(self):
        data = self._image_data()
        self._image_frames = [tk.PhotoImage(data=data, format='gif -index %i' % i) for i in range(30)]
        self._image_index = 0
        self._image = tk.Label(self, image=self._image_frames[0], width='16m')
        self._start_button = tk.Button(self, text='Start', state=tk.DISABLED, command=self._start_device)
        self._stop_button = tk.Button(self, text='Stop', state=tk.DISABLED, command=self._stop_device)
        self._plot_button = tk.Button(self, text='Plot', state=tk.DISABLED, command=self._start_plotter)
        # layout
        self.image.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.BOTH)
        self.start_button.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.BOTH)
        self.stop_button.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.BOTH)
        self.plot_button.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.BOTH)

    def _start_device(self):
        if os.path.exists(self.output) and not self.output_chooser.override:
            answer = self.output_chooser.select()  # try to not override existing file
            if not answer:
                return
        self.output_chooser.override = False
        self._device = api.Chy506R(self.tty, self.output)
        self._device.start()
        self._updatecommand()
        self.after(125, self._watch_device)

    def _stop_device(self):
        if self.device_running():
            self._device.stop()
            self._device.join()
            self._device = None
        self._updatecommand()

    def _start_plotter(self):
        self._plotter = api.Plotter(self.output)
        self._plotter.start()
        self._updatecommand()

    def _stop_plotter(self):
        if self.plotter is not None:
            if self.plotter_running():
                self._plotter.terminate()
            self._plotter = None
            self._updatecommand()

    def _watch_device(self):
        self._updatecommand()
        if self.device_running():
            self.after(125, self._watch_device)
        else:
            if self.device is not None and not self.device.done:
                messagebox.showwarning("Warning", "Measurements aborted. " +
                                       "Is the device connected to PC?")
    @classmethod
    def _image_data(self):
        return images_.spinning_gear

# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=python expandtab tabstop=4 shiftwidth=4:
