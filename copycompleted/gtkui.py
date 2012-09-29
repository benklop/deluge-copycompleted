#
# gtkui.py
#
# Copyright (C) 2012 Calum Lind <calumlind@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
#

import gtk

from deluge.log import LOG as log
from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common

from common import get_resource

class GtkUI(GtkPluginBase):
    def enable(self):
        self.glade = gtk.glade.XML(get_resource("copycompleted_prefs.glade"))
        component.get("Preferences").add_page("Copy Completed", self.glade.get_widget("copycompleted_prefs_box"))
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)
        self.on_show_prefs()

    def disable(self):
        component.get("Preferences").remove_page("Copy Completed")
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)
        del self.glade

    def on_apply_prefs(self):
        log.debug("Applying prefs for Copy Completed")
        if client.is_localhost():
            path = self.glade.get_widget("folderchooser_path").get_current_folder()
        else:
            path = self.glade.get_widget("entry_path").get_text()

        umask = ''.join(map(str, [
            0,
            self.glade.get_widget("spinbutton_umask1").get_value_as_int(),
            self.glade.get_widget("spinbutton_umask2").get_value_as_int(),
            self.glade.get_widget("spinbutton_umask3").get_value_as_int()
            ]))

        config = {
            "copy_to": path,
            "umask": umask,
            "move_to": self.glade.get_widget("radiobutton_move_to").get_active()
        }

        client.copycompleted.set_config(config)

    def on_show_prefs(self):
        if client.is_localhost():
            self.glade.get_widget("folderchooser_path").show()
            self.glade.get_widget("entry_path").hide()
        else:
            self.glade.get_widget("folderchooser_path").hide()
            self.glade.get_widget("entry_path").show()

        def on_get_config(config):
            if client.is_localhost():
                self.glade.get_widget("folderchooser_path").set_current_folder(config["copy_to"])
            else:
                self.glade.get_widget("entry_path").set_text(config["copy_to"])


            umask = map(int, str(config["umask"]))
            self.glade.get_widget("spinbutton_umask1").set_value(umask[1])
            self.glade.get_widget("spinbutton_umask2").set_value(umask[2])
            self.glade.get_widget("spinbutton_umask3").set_value(umask[3])
            self.glade.get_widget("radiobutton_move_to").set_active(config["move_to"])

        client.copycompleted.get_config().addCallback(on_get_config)
