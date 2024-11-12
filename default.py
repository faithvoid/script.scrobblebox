import xbmc
import time
import os

# Path to the .scrobbler.log file (note the leading period)
log_file_path = xbmc.translatePath("Q:\scrobbler.log")

# Function to write the scrobble log in the required format
def write_scrobble_log(song_title, artist_name, album_name, track_pos, duration, rating, timestamp, musicbrainz_id=""):
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n".format(
                artist_name, album_name, song_title, track_pos, duration, rating, timestamp, musicbrainz_id))
    except Exception as e:
        print("Error writing to log file:", e)  # Error message if writing fails

# Check if the log file exists, create if it does not
if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as log_file:
        log_file.write("#AUDIOSCROBBLER/1.1\n")
        log_file.write("#TZ/UTC\n")  # Or #TZ/UTC depending on your timezone setup
        log_file.write("#CLIENT/ScrobbleBox\n")

# Function to convert a MM:SS string to seconds
def convert_time_to_seconds(time_str):
    try:
        minutes, seconds = time_str.split(':')
        return int(minutes) * 60 + int(seconds)
    except ValueError:
        return 0  # In case the time_str is invalid, return 0

# Main loop for monitoring the currently playing track
def monitor_music():
    last_song = None
    player = xbmc.Player()

    while True:
        # Check if something is playing
        if player.isPlaying():
            
            # Retrieve song title, artist, album, track position (time), and duration using xbmc.getInfoLabel()
            current_song = xbmc.getInfoLabel("MusicPlayer.Title")
            current_artist = xbmc.getInfoLabel("MusicPlayer.Artist")
            current_album = xbmc.getInfoLabel("MusicPlayer.Album")
            current_duration = xbmc.getInfoLabel("MusicPlayer.Duration")
            current_track_time = xbmc.getInfoLabel("MusicPlayer.Time")

            # Handle missing track time
            track_pos = convert_time_to_seconds(current_track_time) if current_track_time else 0  # Convert Time to seconds

            # Convert duration to seconds (MM:SS -> total seconds)
            duration = convert_time_to_seconds(current_duration) if current_duration else 0

            # Get the current Unix timestamp
            timestamp = int(time.time())

            # Default rating as 'L' (listened)
            rating = "L"

            # Only log if all required fields are available
            if current_song and current_artist and current_album and current_duration:
                song_info = (current_song, current_artist, current_album, track_pos, duration, rating, timestamp)

                # Check if the song has reached halfway or is finished
                if track_pos >= duration // 2 or track_pos >= duration:
                    # Check if this song is different from the last one (ignoring timestamp)
                    if (current_song, current_artist, current_album) != (last_song[0], last_song[1], last_song[2]) if last_song else True:
                        # Write to the log in the required format
                        write_scrobble_log(current_song, current_artist, current_album, track_pos, duration, rating, timestamp)
                        # Show a notification to the user
                        show_notification("{0} - {1} ({2})".format(current_artist, current_song, current_album))
                        # Update the last song to the current one, but exclude the timestamp
                        last_song = (current_song, current_artist, current_album, track_pos, duration, rating)

        # Sleep for a while before checking again
        time.sleep(5)

# Run the music monitoring function
monitor_music()
