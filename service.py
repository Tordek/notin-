# -*- coding: utf-8 -*-
# slip.dbus.service -- convenience functions for using dbus-activated
# services
#
# Copyright © 2008 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Nils Philippsen <nphilipp@redhat.com>

"""This module contains convenience functions for using dbus-activated services."""

import dbus
import dbus.service

import gobject

__all__ = ['TimeoutObject', 'TimeoutObjectType', 'set_mainloop']

__mainloop__ = None

def __glib_quit_cb__ ():
    global __mainloop__
    # assume a Glib mainloop
    __mainloop__.quit ()

__quit_cb__ = __glib_quit_cb__

def set_mainloop (mainloop):
    global __mainloop__
    __mainloop__ = mainloop

def set_quit_cb (quit_cb):
    global __quit_cb__
    __quit_cb__ = quit_cb

def quit_cb ():
    global __quit_cb__
    __quit_cb__ ()

SENDER_KEYWORD = "__slip_dbus_service_sender__"

def wrap_method (method):
    global SENDER_KEYWORD

    #print "method.__dict__:", method.__dict__

    if method._dbus_sender_keyword != None:
        sender_keyword = method._dbus_sender_keyword
        hide_sender_keyword = False
    else:
        sender_keyword = SENDER_KEYWORD
        hide_sender_keyword = True

    def wrapped_method (self, *p, **k):
        self.sender_seen (k[sender_keyword])

        if hide_sender_keyword:
            del k[sender_keyword]

        retval = method (self, *p, **k)

        self.timeout_restart ()

        return retval

    for attr in filter (lambda x: x[:6] == "_dbus_", dir (method)):
        if attr == "_dbus_sender_keyword":
            wrapped_method._dbus_sender_keyword = sender_keyword
        else:
            setattr (wrapped_method, attr, getattr (method, attr))
        #delattr (method, attr)

    wrapped_method.func_name = method.func_name
    #print "wrapped_method.__dict__:", wrapped_method.__dict__

    return wrapped_method

class TimeoutObjectType (dbus.service.InterfaceType):
    def __new__ (cls, name, bases, dct):
        for attrname, attr in dct.iteritems ():
            if getattr (attr, "_dbus_is_method", False):
                #print "method:", attr
                dct[attrname] = wrap_method (attr)
                #print "wrapped method:", dct[attrname]
        #print "dct:", dct
        return super (TimeoutObjectType, cls).__new__ (cls, name, bases, dct)


class TimeoutObject (dbus.service.Object):
    __metaclass__ = TimeoutObjectType

    live_with_senders = False
    default_duration = 5
    duration = default_duration
    current_source = None
    quit_fn = None
    senders = set ()
    connections_senders = {}
    connections_smobjs = {}

    @classmethod
    def _timeout_cb (cls):
        if len (TimeoutObject.senders) == 0:
            quit_cb ()
            return False

        TimeoutObject.current_source = None
        TimeoutObject.duration = cls.default_duration

        return False

    def _name_owner_changed (self, name, old_owner, new_owner):
        conn = self.connection

        if not new_owner and (old_owner, conn) in TimeoutObject.senders:
            TimeoutObject.senders.remove ((old_owner, conn))
            TimeoutObject.connections_senders[conn].remove (old_owner)

            if len (TimeoutObject.connections_senders[conn]) == 0:
                TimeoutObject.connections_smobjs[conn].remove ()
                del TimeoutObject.connections_senders[conn]
                del TimeoutObject.connections_smobjs[conn]

            if len (TimeoutObject.senders) == 0 and TimeoutObject.current_source == None:
                quit_cb ()

    def timeout_restart (self, duration = None):
        if not duration:
            duration = self.__class__.default_duration
        if not TimeoutObject.duration or duration > TimeoutObject.duration:
            TimeoutObject.duration = duration
        if not TimeoutObject.live_with_senders or len (TimeoutObject.senders) == 0:
            if TimeoutObject.current_source:
                gobject.source_remove (TimeoutObject.current_source)
            TimeoutObject.current_source = gobject.timeout_add (TimeoutObject.duration * 1000, self.__class__._timeout_cb)

    def sender_seen (self, sender):
        if (sender, self.connection) not in TimeoutObject.senders:
            TimeoutObject.senders.add ((sender, self.connection))
            if self.connection not in TimeoutObject.connections_senders.keys ():
                TimeoutObject.connections_senders[self.connection] = set ()
                TimeoutObject.connections_smobjs[self.connection] = \
                        self.connection.add_signal_receiver (
                                handler_function = self._name_owner_changed,
                                signal_name = "NameOwnerChanged",
                                dbus_interface = "org.freedesktop.DBus")
            TimeoutObject.connections_senders[self.connection].add (sender)
