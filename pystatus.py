#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
from enum import Enum
import re


class PlayingState(Enum):
    UNKNOWN = -1
    DEFAULT = 0
    DOWN = 1
    PLAYING = 2
    PAUSED = 3


##
## Configuration
# Colours: colour of widget text corresponding to different playback states
COLOURS = {
    PlayingState.DEFAULT: "#ffffff",
    PlayingState.UNKNOWN: "#ffffff",
    PlayingState.PLAYING: "#1db954",
    PlayingState.PAUSED: "#e3a600",
    PlayingState.DOWN: "#ff0000",
}

# Whether or not to display song progress
SHOW_PROGRESS = True # default True

# The character to use at the start of the widget. Defaults to FontAwesome Spotify logo character.
START_CHAR = {
    PlayingState.DEFAULT: "…  ",
    PlayingState.PLAYING: "♫  ", 
    PlayingState.PAUSED: "⏸  ",
}

# Maximum length of artist + song string. If set to None, no maximum.
# This will always completely remove the song title before truncating the artist.
MAX_LENGTH = 64 # default 64
##
##


def get_from_config_dict(cfg_dict, state):
    try:
        return cfg_dict[state]
    except KeyError:
        return cfg_dict[PlayingState.DEFAULT]


def parse_playerctl(txt):
    ptn = r"^[a-zA-Z0-9_]+ ([a-zA-Z0-9_:]+)\s+(.*)$"
    
    meta = {}
    for match in re.findall(ptn, txt, re.MULTILINE):
        meta[match[0]] = match[1]
    
    return meta

def get_meta() -> dict:
    """Get metadata using playerctl."""
    try:
        status = subprocess.check_output(f"playerctl status", shell=True).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        # No players
        return None

    if status == "Stopped":
        return {
            "status": "Stopped",
        }

    metadata_raw = subprocess.check_output(f"playerctl metadata", shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    meta = parse_playerctl(metadata_raw)

    position = subprocess.check_output(f"playerctl position", shell=True).decode('utf-8')

    meta["status"] = status.strip()
    meta["position"] = position.strip()

    return meta

def print_bar_line(message, state=PlayingState.DEFAULT):
    sys.stdout.write(get_from_config_dict(START_CHAR, state) + message + '\n')
    sys.stdout.flush()

def print_bar_and_colour(message, state=PlayingState.DEFAULT):
    sys.stdout.write(get_from_config_dict(START_CHAR, state) + message + '\n')
    sys.stdout.write(get_from_config_dict(COLOURS, state) + '\n')
    sys.stdout.flush()

def seconds_to_time(timestamp, factor=1):
    """Convert a number in seconds to a human-readable time string, e.g. 67 -> '1:07'."""
    timestamp = int(float(timestamp) / factor)
    secs = timestamp % 60
    mins = timestamp // 60
    return f"{mins:01}:{secs:02}"

def output_unknown():
    """Output for when metadata returns unexpected values."""
    print_bar_and_colour(f"...", PlayingState.UNKNOWN)

def main():
    meta = get_meta()

    if meta is None:
        # Spotify is not running
        print_bar_and_colour(f"down", PlayingState.DOWN)
    elif meta["status"] == "Stopped":
        print_bar_and_colour(f"stopped", PlayingState.DOWN)
    else:
        title = meta.get("xesam:title", None)
        artist = meta.get("xesam:artist", None)

        if title is None:
            # something is wrong with the metadata
            output_unknown()
            return

        if artist is None:
            # this is probably a podcast 
            artist = meta.get("xesam:album", None)
            if artist is None:
                # something is wrong with the metadata
                output_unknown()
                return

        song_string = f"{artist} — {title}"

        # song string truncation
        if MAX_LENGTH is not None and len(song_string) > MAX_LENGTH:
            song_string = song_string[:MAX_LENGTH - 1] + "…"

        # song progress calculation
        if SHOW_PROGRESS:
            position = seconds_to_time(meta.get("position", 0))
            length = seconds_to_time(meta.get("mpris:length", 0), factor=1e6)
            bar_line = f"{song_string} ({position} / {length})"
        else:
            bar_line = f"{song_string}"

        # play/pause status display
        status = meta.get("status")
        if status == "Playing":
            print_bar_and_colour(bar_line, PlayingState.PLAYING)
        elif status == "Paused":
            print_bar_and_colour(bar_line, PlayingState.PAUSED)
        else:
            print_bar_and_colour(bar_line, PlayingState.UNKNOWN)


if __name__ == '__main__':
    main()
