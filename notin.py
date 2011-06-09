#!/usr/bin/python

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

import service

import random

class MessageQueue(object):
    def __init__(self):
        self.messages = {}
        self.queue = []
        self.current_message = None

    def enqueue(self, replaces_id, message):
        if replaces_id in self.messages:
            self.messages[replaces_id] = message
            return replaces_id

        key = random.randint(0, 65535)

        while key in self.messages:
            key = random.rand()

        self.messages[key] = message
        self.queue.append(key)

        return key

    def dequeue(self, message_id):
        if self.current_message == message_id:
            self.current_message = None
            if not self.queue:
                print
        else:
            self.queue.remove(message_id)

        del self.messages[message_id]

    def expired_message(self, message_id, delta):
        message = self.messages[message_id]

        if message["expire_timeout"] != 0:
            if message["expire_timeout"] == -1:
                message["expire_timeout"] = 3000000

            message["expire_timeout"] -= 1000 * delta
            if message["expire_timeout"] <= 0:
                return True

        return False

    def update(self, delta):
        if not (self.current_message or self.queue):
            return True

        if self.current_message:
            if self.expired_message(self.current_message, delta):
                self.dequeue(self.current_message)
                self.current_message = None
                if not queue:
                    print

        if self.queue:
            if self.current_message:
                self.queue.append(self.current_message)

            self.current_message = self.queue.pop(0)
            print (u"%(app_name)s: %(body)s" % self.messages[self.current_message]).encode('utf-8')


        return True


class Notin(service.TimeoutObject):
    def __init__(self, queue, *p, **k):
        super(Notin, self).__init__(*p, **k)
        self.queue = queue

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='as', in_signature='')
    def GetCapabilities(self):
        return ["body"]

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='u', in_signature='susssasa{ss}u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        notification = {"app_name": app_name,
                        "replaces_id": replaces_id,
                        "app_icon": app_icon,
                        "summary": summary,
                        "body": body,
                        "actions": actions,
                        "hints": hints,
                        "expire_timeout": expire_timeout}

        return self.queue.enqueue(replaces_id, notification)

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='', in_signature='u')
    def CloseNotification(self, notification_id):
        self.queue.dequeue(notification_id)
        return

    @dbus.service.method("org.freedesktop.Notifications",
                         out_signature='', in_signature='ssss')
    def GetServerInformation(self, name, vendor, version, spec_version):
        #TODO: handle out parameters?
        return

    @dbus.service.signal("org.freedesktop.Notifications",
                         signature='uu')
    def NotificationClosed(self, id, reason):
        return

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    queue = MessageQueue()
    system_bus = dbus.SessionBus()

    name = dbus.service.BusName("org.freedesktop.Notifications", system_bus)
    obj = Notin(queue, system_bus, '/org/freedesktop/Notifications')

    mainloop = gobject.MainLoop()
    service.set_mainloop(mainloop)

    gobject.timeout_add(1000, lambda: queue.update(1000))
    mainloop.run()
