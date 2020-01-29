#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from dialogs.dialog import Dialog

import os.path


class OpenNotebookDialog(Dialog):
    ''' File chooser for opening notebooks '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        response = self.view.run()
        if response == Gtk.ResponseType.OK:
            return_value = self.view.get_filename()
        else:
            return_value = None
        self.close()
        return return_value

    def setup(self):
        action = Gtk.FileChooserAction.OPEN
        buttons = ('_Cancel', Gtk.ResponseType.CANCEL, '_Open', Gtk.ResponseType.OK)
        self.view = Gtk.FileChooserDialog('Open notebook', self.main_window, action, buttons)
    
        for widget in self.view.get_header_bar().get_children():
            if isinstance(widget, Gtk.Button) and widget.get_label() == '_Open':
                widget.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
                widget.set_can_default(True)
                widget.grab_default()

        # file filtering
        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.ipynb')
        file_filter1.set_name('Jupyter Notebooks')
        self.view.add_filter(file_filter1)
        
        self.view.set_select_multiple(False)


