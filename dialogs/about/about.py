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


class AboutDialog(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.show_all()
        del(self.view)

    def setup(self):
        self.view = Gtk.AboutDialog()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_program_name('Porto')
        self.view.set_version('0.0.2')
        self.view.set_copyright('Copyright © 2017-2020 - the Porto developers')
        self.view.set_comments('Porto is a notebook style interface to Python and SageMath. It is designed to make exploring mathematics easy and fun.')
        self.view.set_license_type(Gtk.License.GPL_3_0)
        self.view.set_website('https://www.cvfosammmm.org/porto/')
        self.view.set_website_label('https://www.cvfosammmm.org/porto/')
        self.view.set_authors(('Robert Griesel',))
        logo = Gtk.Image.new_from_file(os.path.dirname(os.path.realpath(__file__)) + '/../../resources/images/org.cvfosammmm.Porto.svg')
        self.view.set_logo(logo.get_pixbuf())
        

