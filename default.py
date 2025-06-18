import xbmc
import xbmcaddon
import xbmcgui
import time
import os

ADDON = xbmcaddon.Addon(id='script.scrobblebox')

# Hardcoded path for icon in Xbox filesystem
ICON_PATH = os.path.join(os.path.dirname(__file__), "icon-scrobblebox.png")

# Path to the scrobbler log
log_file_path = xbmc.translatePath("Q:\\scrobbler.log")

# Load user setting for notifications
show_notifications_setting = ADDON.getSetting("show_notifications") == "true"

# Write scrobble log in Rockbox format
def write_scrobble_log(song_title, artist_name, album_name, track_number, duration, rating, timestamp):
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(
                artist_name, album_name, song_title, track_number, duration, rating, timestamp))
    except Exception as e:
        print("Error writing to log file: {0}".format(e))

# Ensure the log file exists and is initialized
if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as log_file:
        log_file.write("#AUDIOSCROBBLER/1.1\n")
        log_file.write("#TZ/UTC\n")
        log_file.write("#CLIENT/ScrobbleBox\n")

# Convert MM:SS string to seconds
def convert_time_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except:
        return 0

# Show notification if enabled
def show_notification(message):
    if show_notifications_setting:
            xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Logged: {0}", 5, "{1}")'.format(message, ICON_PATH))

# Monitor music playback and log scrobbles
def monitor_music():
    last_song = None
    player = xbmc.Player()

    while True:
        if player.isPlaying():
            current_song = xbmc.getInfoLabel("MusicPlayer.Title")
            current_artist = xbmc.getInfoLabel("MusicPlayer.Artist")
            current_album = xbmc.getInfoLabel("MusicPlayer.Album")
            current_duration = xbmc.getInfoLabel("MusicPlayer.Duration")
            current_track_time = xbmc.getInfoLabel("MusicPlayer.Time")
            current_track_number = xbmc.getInfoLabel("MusicPlayer.TrackNumber")

            duration = convert_time_to_seconds(current_duration)
            track_pos = convert_time_to_seconds(current_track_time)
            try:
                track_number = int(current_track_number)
            except:
                track_number = 0

            timestamp = int(time.mktime(time.gmtime()))
            rating = "L"

            if current_song and current_artist and current_album and duration > 30:
                song_key = (current_song, current_artist, current_album, track_number)
                if (track_pos >= duration // 2 or track_pos >= 240):
                    if last_song != song_key:
                        write_scrobble_log(current_song, current_artist, current_album,
                                           track_number, duration, rating, timestamp)
                        show_notification("{0} - {1} ({2})".format(current_artist, current_song, current_album))
                        last_song = song_key
        time.sleep(5)

# Start
monitor_music()
