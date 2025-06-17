import xbmc
import time
import os

# Path to the .scrobbler.log file
log_file_path = xbmc.translatePath("Q:\\scrobbler.log")

# Function to write the scrobble log in the required Rockbox format
def write_scrobble_log(song_title, artist_name, album_name, track_number, duration, rating, timestamp):
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(
                artist_name, album_name, song_title, track_number, duration, rating, timestamp))
    except Exception as e:
        print("Error writing to log file: {0}".format(e))

# Ensure the log file exists and contains the proper header
if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as log_file:
        log_file.write("#AUDIOSCROBBLER/1.1\n")
        log_file.write("#TZ/UTC\n")
        log_file.write("#CLIENT/ScrobbleBox\n")

# Helper function to convert MM:SS string to seconds
def convert_time_to_seconds(time_str):
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        return 0
    except ValueError:
        return 0

def show_notification(message):
    xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Logged: {0}", 5000)'.format(message))

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

            # Convert fields
            duration = convert_time_to_seconds(current_duration) if current_duration else 0
            track_pos = convert_time_to_seconds(current_track_time) if current_track_time else 0
            try:
                track_number = int(current_track_number)
            except:
                track_number = 0

            # Use UTC timestamp
            timestamp = int(time.mktime(time.gmtime()))

            # Default rating
            rating = "L"

            # Only log valid entries
            if current_song and current_artist and current_album and duration > 30:
                song_key = (current_song, current_artist, current_album, track_number)

                # Only log if it's played long enough and not already logged
                if (track_pos >= duration // 2 or track_pos >= 240):
                    if last_song != song_key:
                        write_scrobble_log(current_song, current_artist, current_album,
                                           track_number, duration, rating, timestamp)
                        show_notification("{0} - {1} ({2})".format(current_artist, current_song, current_album))
                        last_song = song_key

        time.sleep(5)

# Start the music monitor
monitor_music()
