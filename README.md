# py3musicstatus - Spotify widget for py3status bar for i3 window manager

This is a widget for the py3status for i3 which displays the current playing song and artist, and the current progress through the song. It makes uses of the playerctl tool.

Bug reports and pull requests are welcome! I will attempt to respond as soon as possible.

## Requirements

* [py3status](https://py3status.readthedocs.io/en/latest/user-guide/installation/)
* playerctl
* A music player

The other requirements are dbus and Python 3, which you shouldn't need to worry about since they come bundled with most distros. You also need [i3](https://i3wm.org), obviously.

## Installation

* Clone repository to your preferred location
* Update your `i3status.conf` with
```conf
order += "external_script"

# ...

external_script {
    script_path = "/path/to/py3musicstatus/pystatus.py"
    cache_timeout = 1
}
```

## Configuration

There are some options you can set at the top of the `pystatus.py` script by editing it. They are documented in the script.
