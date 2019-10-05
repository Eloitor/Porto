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
from gi.repository import Gio

import viewgtk.viewgtk_worksheet_list as viewgtk_worksheet_list


class HeaderBar(Gtk.Paned):
    ''' Title bar of the app, contains always visible controls, 
        worksheet title and state (computing, idle, ...) '''
        
    def __init__(self, button_layout):
        Gtk.Paned.__init__(self)
        
        show_close_button = True if (button_layout.find('close') < button_layout.find(':') and button_layout.find('close') >= 0) else False
        self.hb_left = HeaderBarLeft(show_close_button)
        
        show_close_button = True if (button_layout.find('close') > button_layout.find(':') and button_layout.find('close') >= 0) else False
        self.hb_right = HeaderBarRight(show_close_button)

        self.pack1(self.hb_left, False, False)
        self.pack2(self.hb_right, True, False)
        
    def set_title(self, text):
        self.hb_right.set_title(text)

    def set_subtitle(self, text):
        self.hb_right.set_subtitle(text)

    def get_subtitle(self):
        return self.hb_right.get_subtitle()
        
    def activate_stop_button(self):
        self.hb_right.stop_button.set_sensitive(True)

    def deactivate_stop_button(self):
        self.hb_right.stop_button.set_sensitive(False)

    def activate_up_button(self):
        self.hb_right.up_button.set_sensitive(True)

    def deactivate_up_button(self):
        self.hb_right.up_button.set_sensitive(False)

    def activate_down_button(self):
        self.hb_right.down_button.set_sensitive(True)

    def deactivate_down_button(self):
        self.hb_right.down_button.set_sensitive(False)

    def activate_save_button(self):
        self.hb_right.save_button.set_sensitive(True)

    def deactivate_save_button(self):
        self.hb_right.save_button.set_sensitive(False)

    def activate_revert_button(self):
        self.hb_right.revert_button.set_sensitive(True)

    def deactivate_revert_button(self):
        self.hb_right.revert_button.set_sensitive(False)

    def activate_documentation_mode(self):
        if self.hb_right.save_button.get_parent() == None:
            self.hb_right.remove(self.hb_right.revert_button)
            self.hb_right.pack_end(self.hb_right.save_button)

    def deactivate_documentation_mode(self):
        if self.hb_right.revert_button.get_parent() == None:
            self.hb_right.remove(self.hb_right.save_button)
            self.hb_right.pack_end(self.hb_right.revert_button)


class HeaderBarLeft(Gtk.HeaderBar):

    def __init__(self, show_close_button):
        Gtk.HeaderBar.__init__(self)

        self.set_show_close_button(show_close_button)

        self.create_buttons()

    def create_buttons(self):
        self.ws_add_wrapper = Gtk.HBox()
        self.create_ws_button = Gtk.Button.new_from_icon_name('document-new-symbolic', Gtk.IconSize.BUTTON)
        self.create_ws_button.set_tooltip_text('Create new worksheet')
        self.create_ws_button.set_focus_on_click(False)
        self.pack_start(self.create_ws_button)
        self.open_ws_button = Gtk.Button.new_from_icon_name('document-open-symbolic', Gtk.IconSize.BUTTON)
        self.open_ws_button.set_tooltip_text('Open worksheet')
        self.open_ws_button.set_focus_on_click(False)
        self.pack_start(self.open_ws_button)

        self.search_button = Gtk.Button.new_from_icon_name('system-search-symbolic', Gtk.IconSize.BUTTON)
        self.search_button.set_tooltip_text('Search')
        self.search_button.set_focus_on_click(False)
        #self.search_button.set_sensitive(False)
        #self.pack_end(self.search_button)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 250, 250
    

class HeaderBarRight(Gtk.HeaderBar):

    def __init__(self, show_close_button):
        Gtk.HeaderBar.__init__(self)

        self.set_show_close_button(show_close_button)
        self.props.title = ''
        self.open_worksheets_number = 0
        
        self.create_buttons()
        self.pack_buttons()

    def create_buttons(self):
        self.worksheet_chooser = WorksheetChooser()
        self.open_worksheets_button_label = Gtk.Label('Worksheets')
        self.open_worksheets_button_box = Gtk.HBox()
        self.open_worksheets_button_box.pack_start(Gtk.Image.new_from_icon_name('document-open-symbolic', Gtk.IconSize.MENU), False, False, 0)
        self.open_worksheets_button_box.pack_start(self.open_worksheets_button_label, False, False, 0)
        self.open_worksheets_button_box.pack_start(Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU), False, False, 0)
        self.open_worksheets_button = Gtk.MenuButton()
        self.open_worksheets_button.set_can_focus(False)
        self.open_worksheets_button.set_use_popover(True)
        self.open_worksheets_button.add(self.open_worksheets_button_box)
        self.open_worksheets_button.get_style_context().add_class("text-button")
        self.open_worksheets_button.get_style_context().add_class("image-button")
        self.open_worksheets_button.set_popover(self.worksheet_chooser)

        self.add_cell_box = Gtk.HBox()
        self.add_cell_box.get_style_context().add_class('linked')

        self.add_codecell_button = Gtk.Button.new_from_icon_name('add-codecell-symbolic', Gtk.IconSize.BUTTON)
        self.add_codecell_button.set_tooltip_text('Add code cell below (Alt+Return)')
        self.add_codecell_button.set_focus_on_click(False)
        self.add_cell_box.add(self.add_codecell_button)
        self.add_markdowncell_button = Gtk.Button.new_from_icon_name('add-markdowncell-symbolic', Gtk.IconSize.BUTTON)
        self.add_markdowncell_button.set_tooltip_text('Add markdown cell below (Ctrl+M)')
        self.add_markdowncell_button.set_focus_on_click(False)
        self.add_cell_box.add(self.add_markdowncell_button)
        
        self.move_cell_box = Gtk.HBox()
        self.move_cell_box.get_style_context().add_class('linked')
        self.up_button = Gtk.Button.new_from_icon_name('up-button-symbolic', Gtk.IconSize.BUTTON)
        self.up_button.set_tooltip_text('Move cell up (Ctrl+Up)')
        self.up_button.set_focus_on_click(False)
        self.up_button.set_sensitive(False)
        self.move_cell_box.add(self.up_button)
        self.down_button = Gtk.Button.new_from_icon_name('down-button-symbolic', Gtk.IconSize.BUTTON)
        self.down_button.set_tooltip_text('Move cell down (Ctrl+Down)')
        self.down_button.set_focus_on_click(False)
        self.down_button.set_sensitive(False)
        self.move_cell_box.add(self.down_button)
        self.delete_button = Gtk.Button.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON)
        self.delete_button.set_tooltip_text('Delete cell (Ctrl+Backspace)')
        self.delete_button.set_focus_on_click(False)
        self.move_cell_box.add(self.delete_button)

        self.eval_box = Gtk.HBox()
        self.eval_box.get_style_context().add_class('linked')
        self.eval_button = Gtk.Button.new_from_icon_name('eval-button-symbolic', Gtk.IconSize.BUTTON)
        self.eval_button.set_tooltip_text('Evaluate Cell (Shift+Return)')
        self.eval_button.set_focus_on_click(False)
        self.eval_box.add(self.eval_button)
        self.eval_nc_button = Gtk.Button.new_from_icon_name('eval-nc-button-symbolic', Gtk.IconSize.BUTTON)
        self.eval_nc_button.set_tooltip_text('Evaluate Cell, then Go to next Cell (Ctrl+Return)')
        self.eval_nc_button.set_focus_on_click(False)
        self.eval_box.add(self.eval_nc_button)
        self.stop_button = Gtk.Button.new_from_icon_name('media-playback-stop-symbolic', Gtk.IconSize.BUTTON)
        self.stop_button.set_tooltip_text('Stop Evaluation (Ctrl+H)')
        self.stop_button.set_focus_on_click(False)
        self.stop_button.set_sensitive(False)
        self.eval_box.add(self.stop_button)

        self.show_sidebar_button = Gtk.ToggleButton()
        self.show_sidebar_button.set_image(Gtk.Image.new_from_icon_name('view-list-symbolic', Gtk.IconSize.MENU))
        self.show_sidebar_button.set_tooltip_text('Show sidebar')
        self.show_sidebar_button.set_focus_on_click(False)

        self.create_full_hamburger_menu()
        self.create_blank_hamburger_menu()
        
        self.save_button = Gtk.Button()
        self.save_button.set_label('Save')
        self.save_button.set_tooltip_text('Save the currently opened file')
        self.save_button.set_focus_on_click(False)

        self.revert_button = Gtk.Button()
        self.revert_button.set_label('Revert Changes')
        self.revert_button.set_tooltip_text('Set worksheet back to it\'s original state')
        self.revert_button.set_focus_on_click(False)

    def create_full_hamburger_menu(self):
        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.BUTTON)
        self.menu_button.set_image(image)
        self.menu_button.set_focus_on_click(False)
        self.options_menu = Gio.Menu()

        kernel_section = Gio.Menu()
        item = Gio.MenuItem.new('Restart Language Kernel', 'app.restart_kernel')
        kernel_section.append_item(item)
        self.change_kernel_menu = Gio.Menu()
        kernel_section.append_submenu('Change Language', self.change_kernel_menu)

        save_section = Gio.Menu()
        item = Gio.MenuItem.new('Save As ...', 'app.save_as')
        save_section.append_item(item)
        item = Gio.MenuItem.new('Save All', 'app.save_all')
        save_section.append_item(item)

        worksheet_section = Gio.Menu()
        item = Gio.MenuItem.new('Delete Worksheet ...', 'app.delete_worksheet')
        worksheet_section.append_item(item)

        close_section = Gio.Menu()
        item = Gio.MenuItem.new('Close', 'app.close_worksheet')
        close_section.append_item(item)
        item = Gio.MenuItem.new('Close All', 'app.close_all_worksheets')
        close_section.append_item(item)

        self.options_menu.append_section(None, kernel_section)
        self.options_menu.append_section(None, save_section)
        self.options_menu.append_section(None, worksheet_section)
        self.options_menu.append_section(None, close_section)

        view_section = Gio.Menu()
        view_menu = Gio.Menu()
        view_menu.append_item(Gio.MenuItem.new('Show Sidebar', 'app.toggle-sidebar'))
        view_section.append_submenu('View', view_menu)
        self.options_menu.append_section(None, view_section)
        preferences_section = Gio.Menu()
        item = Gio.MenuItem.new('Preferences', 'app.show_preferences_dialog')
        preferences_section.append_item(item)
        self.options_menu.append_section(None, preferences_section)
        meta_section = Gio.Menu()
        item = Gio.MenuItem.new('Keyboard Shortcuts', 'app.show_shortcuts_window')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('About', 'app.show_about_dialog')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('Quit', 'app.quit')
        meta_section.append_item(item)
        self.options_menu.append_section(None, meta_section)

        self.menu_button.set_menu_model(self.options_menu)

    def create_blank_hamburger_menu(self):
        self.blank_menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.BUTTON)
        self.blank_menu_button.set_image(image)
        self.blank_menu_button.set_focus_on_click(False)
        self.blank_options_menu = Gio.Menu()

        view_section = Gio.Menu()
        view_menu = Gio.Menu()
        view_menu.append_item(Gio.MenuItem.new('Show Sidebar', 'app.toggle-sidebar'))
        view_section.append_submenu('View', view_menu)
        self.blank_options_menu.append_section(None, view_section)
        preferences_section = Gio.Menu()
        item = Gio.MenuItem.new('Preferences', 'app.show_preferences_dialog')
        preferences_section.append_item(item)
        self.blank_options_menu.append_section(None, preferences_section)
        meta_section = Gio.Menu()
        item = Gio.MenuItem.new('Keyboard Shortcuts', 'app.show_shortcuts_window')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('About', 'app.show_about_dialog')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('Quit', 'app.quit')
        meta_section.append_item(item)
        self.blank_options_menu.append_section(None, meta_section)

        self.blank_menu_button.set_menu_model(self.blank_options_menu)

    def pack_buttons(self):
        self.pack_start(self.open_worksheets_button)
        self.pack_start(self.add_cell_box)
        self.pack_start(self.move_cell_box)
        self.pack_start(self.eval_box)
        self.pack_end(self.menu_button)
        self.pack_end(self.blank_menu_button)
        self.pack_end(self.save_button)
        self.show_all()

    def show_buttons(self):
        self.add_cell_box.show_all()
        self.move_cell_box.show_all()
        self.eval_box.show_all()
        self.menu_button.show_all()
        self.blank_menu_button.hide()
        self.save_button.show_all()

    def hide_buttons(self):
        self.add_cell_box.hide()
        self.move_cell_box.hide()
        self.eval_box.hide()
        self.menu_button.hide()
        self.blank_menu_button.show_all()
        self.save_button.hide()

    def increment_worksheets_number(self):
        self.open_worksheets_number += 1
        self.open_worksheets_button_label.set_text('Worksheets (' + str(self.open_worksheets_number) + ')')

    def decrement_worksheets_number(self):
        self.open_worksheets_number -= 1
        if self.open_worksheets_number == 0:
            self.open_worksheets_button_label.set_text('Worksheets')
        else:
            self.open_worksheets_button_label.set_text('Worksheets (' + str(self.open_worksheets_number) + ')')

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 763, 763


class WorksheetChooser(Gtk.Popover):
    
    def __init__(self):
        Gtk.Popover.__init__(self)
        self.get_style_context().add_class('hb')
        self.set_size_request(300, -1)

        self.box = Gtk.VBox()

        self.open_worksheets_list_view = viewgtk_worksheet_list.WorksheetListOpenView()
        self.open_worksheets_list_view.set_can_focus(False)
        self.open_worksheets_label_revealer = Gtk.Revealer()
        self.open_worksheets_label = Gtk.Label('Open Worksheets')
        self.open_worksheets_label.set_xalign(0)
        self.open_worksheets_label.get_style_context().add_class('wslist_header')
        self.open_worksheets_label_revealer.add(self.open_worksheets_label)
        self.open_worksheets_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.get_style_context().add_class('wslist_top')

        self.recent_worksheets_list_view = viewgtk_worksheet_list.WorksheetListRecentView()
        self.recent_worksheets_list_view.set_selection_mode(Gtk.SelectionMode.NONE)
        self.recent_worksheets_list_view.set_can_focus(False)
        self.recent_worksheets_label_revealer = Gtk.Revealer()
        self.recent_worksheets_label = Gtk.Label('Recently Opened Worksheets')
        self.recent_worksheets_label.set_xalign(0)
        self.recent_worksheets_label.get_style_context().add_class('wslist_header')
        self.recent_worksheets_label_revealer.add(self.recent_worksheets_label)
        self.recent_worksheets_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)

        self.open_worksheets_list_view_wrapper = Gtk.ScrolledWindow()
        self.open_worksheets_list_view_wrapper.add(self.open_worksheets_list_view)
        self.open_worksheets_list_view_wrapper.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.recent_worksheets_list_view_wrapper = Gtk.ScrolledWindow()
        self.recent_worksheets_list_view_wrapper.add(self.recent_worksheets_list_view)
        self.recent_worksheets_list_view_wrapper.set_size_request(-1, 247)
        
        self.box.pack_start(self.open_worksheets_label_revealer, False, False, 0)
        self.box.pack_start(self.open_worksheets_list_view_wrapper, False, False, 0)
        self.box.pack_start(self.recent_worksheets_label_revealer, False, False, 0)
        self.box.pack_start(self.recent_worksheets_list_view_wrapper, True, True, 0)

        self.button_box = Gtk.HBox()
        self.button_box.get_style_context().add_class('linked')
        self.button_box.set_margin_top(12)
        self.button_box.set_margin_bottom(3)
        self.create_button = Gtk.Button.new_with_label('Create Worksheet')
        self.open_button = Gtk.Button.new_with_label('Open Worksheet')
        self.button_box.pack_start(self.open_button, False, False, 0)
        self.button_box.pack_start(self.create_button, False, False, 0)
        self.box.pack_start(self.button_box, False, False, 0)

        self.box.show_all()
        self.add(self.box)

