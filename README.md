notin'
======

`notin'` is a small notifications D-BUS listener implementing the
org.fredesktop.Notifications [protocol][protocol].

`notin'` simply listens for any notifications, and outputs them to `stdout`.
It's meant as a simple companion for an [XMonad][xmonad] or similar tiling
window manager, redirecting its output to dzen, as a small and unobtrusive
notifications bar.

Testing notin'
==============

Just call `python notin.py`, and cause a notification to happen: Flip a song
on Amarok, get a message from Kopete, or call `notify-send foo`, and you'll
see your message appear on notin's output.

Using notin'
============

Notin's meant to be used with a [dzen][dzen] window: just pipe its output through:

`python notin.py | dzen2`

Your notifications will appear on your dzen bar.

[protocol]: http://www.galago-project.org/specs/notification/0.9/x408.html
[xmonad]: http://xmonad.org/
[dzen]: http://sites.google.com/site/gotmor/dzen
