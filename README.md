notin'
======

`notin'` is a small notifications D-BUS listener implementing the
org.fredesktop.Notifications [protocol][protocol].

`notin'` simply listens for any notifications, and outputs them to `stdout`.
It's meant as a simple companion for an [XMonad][xmonad] or similar tiling
window manager, redirecting its output to dzen, as a small and unobtrusive
notifications bar.


[protocol]: http://www.galago-project.org/specs/notification/0.9/x408.html
[xmonad]: http://xmonad.org/
