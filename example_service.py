#!/usr/bin/python

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

import service

class DemoException(dbus.DBusException):
    _dbus_error_name = 'org.fedoraproject.slip.Example.DemoException'

class SomeObject(service.TimeoutObject):
    def __init__(self, *p, **k):
        super(SomeObject, self).__init__(*p, **k)
        print "service object constructed"

    def __del__(self):
        print "service object deleted"

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='as', in_signature='')
    def GetCapabilities(self):
        print "GetCapabilities"
        return ["body"]

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='u', in_signature='susssasa{ss}u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        print "%s: %s"%(app_name, body)
        return 1

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='', in_signature='u')
    def CloseNotification(self, notification_id):
        print "CloseNotification"
        return ("Hello Tuple", " from example-service.py")

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='', in_signature='sss')
    def GetServerInformation(self, name, vendor, version):
        print "GetServerInformation"
        return {"first": "Hello Dict", "second": " from example-service.py"}

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='', in_signature='uu')
    def NotificationClosed(self, id, reason):
        return

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    system_bus = dbus.SessionBus()

    name = dbus.service.BusName("org.freedesktop.Notifications", system_bus)
    obj = SomeObject(system_bus, '/org/freedesktop/Notifications')

    mainloop = gobject.MainLoop()
    service.set_mainloop(mainloop)
    print "Running example service."
    mainloop.run()
