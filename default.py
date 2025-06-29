import xbmc
import xbmcaddon
import xbmcgui
import time
import os
import hashlib
import urllib
import urllib2
import json

ADDON = xbmcaddon.Addon(id='script.scrobblebox')

# Hardcoded path for icons
ICON_PATH = os.path.join(os.path.dirname(__file__), "icon-scrobblebox.png")
LASTFM_ICON = os.path.join(os.path.dirname(__file__), "icon-lastfm.png")
LIBREFM_ICON = os.path.join(os.path.dirname(__file__), "icon-librefm.png") # Deprecated
LISTENBRAINZ_ICON = os.path.join(os.path.dirname(__file__), "icon-listenbrainz.png") # Deprecated

# Path to the scrobbler log
log_folder = ADDON.getSetting("log_folder")
log_file_path = os.path.join(log_folder, "scrobbler.log")

# Load user settings
show_notifications_setting = ADDON.getSetting("show_notifications") == "true"
# Last.fm settings
lastfm_api_key     = ADDON.getSetting("lastfm_api_key")
lastfm_api_secret  = ADDON.getSetting("lastfm_api_secret")
lastfm_username    = ADDON.getSetting("lastfm_username")
lastfm_password    = ADDON.getSetting("lastfm_password")
lastfm_upload      = ADDON.getSetting("lastfm_upload") == "true"
lastfm_upload_listening = ADDON.getSetting("lastfm_upload_listening") == "true"
# Libre.fm settings (deprecated)
librefm_api_key     = ADDON.getSetting("librefm_api_key")
librefm_api_secret  = ADDON.getSetting("librefm_api_secret")
librefm_username    = ADDON.getSetting("librefm_username")
librefm_password    = ADDON.getSetting("librefm_password")
librefm_upload      = ADDON.getSetting("librefm_upload") == "true"
librefm_upload_listening = ADDON.getSetting("librefm_upload_listening") == "true"
# ListenBrainz settings
listenbrainz_user_token = ADDON.getSetting("listenbrainz_user_token")
listenbrainz_upload = ADDON.getSetting("listenbrainz_upload") == "true"
listenbrainz_upload_listening = ADDON.getSetting("listenbrainz_upload_listening") == "true"
# Maloja settings
maloja_api_url = ADDON.getSetting("maloja_api_url")
maloja_api_key = ADDON.getSetting("maloja_api_key")
maloja_upload = ADDON.getSetting("maloja_upload") == "true"
maloja_upload_listening = ADDON.getSetting("maloja_upload_listening") == "true"

def md5(s):
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return hashlib.md5(s).hexdigest()

def generate_api_sig(params, api_secret):
    keys = sorted(params.keys())
    sig = b""
    for key in keys:
        key_str = key.encode('utf-8') if isinstance(key, unicode) else str(key)
        val = params[key]
        val_str = val.encode('utf-8') if isinstance(val, unicode) else str(val)
        sig += key_str + val_str
    if isinstance(api_secret, unicode):
        api_secret = api_secret.encode('utf-8')
    sig += api_secret
    return md5(sig)

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

# Show notifications if enabled
def show_notification(message, icon=ICON_PATH):
    if show_notifications_setting:
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "%s", 5000, "%s")' % (message, icon))

# Get session key from Last.fm
def get_session_key(api_key, api_secret, username, password):
    try:
        # Ensure all values are UTF-8 encoded strings
        def encode(val):
            if isinstance(val, unicode):
                return val.encode('utf-8')
            return str(val)
        params = {
            'api_key': encode(api_key),
            'method': 'auth.getMobileSession',
            'password': encode(password),  # IMPORTANT: plaintext, not MD5!
            'username': encode(username),
        }
        # Build API signature: concat all params (alphabetical order), then append secret, then md5
        sig_str = ''.join([k + params[k] for k in sorted(params)]) + api_secret
        api_sig = hashlib.md5(sig_str.encode('utf-8')).hexdigest()
        params['api_sig'] = api_sig
        params['format'] = 'json'
        data = urllib.urlencode(params)
        url = 'https://ws.audioscrobbler.com/2.0/'
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        result = json.loads(response.read())
        print("Last.fm response:", result)
        if "session" in result and "key" in result["session"]:
            return result['session']['key']
        else:
            raise Exception("No session key in response: %s" % result)
    except urllib2.HTTPError as e:
        error_msg = e.read()
        print("HTTPError %s: %s" % (e.code, error_msg))
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "HTTP %s: %s", 10000, "%s")' % (e.code, error_msg, LASTFM_ICON))
        raise
    except Exception as e:
        print("Exception:", str(e))
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Auth error: %s", 10000, "%s")' % (e, LASTFM_ICON))
        raise

# Get session key from Libre.fm
def get_session_key_librefm(api_key, api_secret, username, password):
    try:
        # Ensure all values are UTF-8 encoded strings
        def encode(val):
            if isinstance(val, unicode):
                return val.encode('utf-8')
            return str(val)
        params = {
            'api_key': encode(api_key),
            'method': 'auth.getMobileSession',
            'password': encode(password),  # IMPORTANT: plaintext, not MD5!
            'username': encode(username),
        }
        # Build API signature: concat all params (alphabetical order), then append secret, then md5
        sig_str = ''.join([k + params[k] for k in sorted(params)]) + api_secret
        api_sig = hashlib.md5(sig_str.encode('utf-8')).hexdigest()
        params['api_sig'] = api_sig
        params['format'] = 'json'
        data = urllib.urlencode(params)
        url = 'https://libre.fm/2.0/'
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        result = json.loads(response.read())
        print("Last.fm response:", result)
        if "session" in result and "key" in result["session"]:
            return result['session']['key']
        else:
            raise Exception("No session key in response: %s" % result)
    except urllib2.HTTPError as e:
        error_msg = e.read()
        print("HTTPError %s: %s" % (e.code, error_msg))
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "HTTP %s: %s", 10000, "%s")' % (e.code, error_msg, LIBREFM_ICON))
        raise
    except Exception as e:
        print("Exception:", str(e))
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Auth error: %s", 10000, "%s")' % (e, LIBREFM_ICON))
        raise

# Get session key from Maloja
def get_session_key_maloja(api_key, api_secret, username, password, api_url):
    try:
        def encode(val):
            if isinstance(val, unicode):
                return val.encode('utf-8')
            return str(val)
        params = {
            'api_key': encode(api_key),
            'method': 'auth.getMobileSession',
            'password': encode(password),
            'username': encode(username),
        }
        sig_str = ''.join([k + params[k] for k in sorted(params)]) + api_secret
        api_sig = hashlib.md5(sig_str.encode('utf-8')).hexdigest()
        params['api_sig'] = api_sig
        params['format'] = 'json'
        data = urllib.urlencode(params)
        req = urllib2.Request(api_url, data)
        response = urllib2.urlopen(req)
        result = json.loads(response.read())
        print("Maloja response:", result)
        if "session" in result and "key" in result["session"]:
            return result['session']['key']
        else:
            raise Exception("No session key in response: %s" % result)
    except urllib2.HTTPError as e:
        error_msg = e.read()
        print("HTTPError %s: %s" % (e.code, error_msg))
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "HTTP %s: %s", 10000, "%s")' % (e.code, error_msg, LASTFM_ICON))
        raise
    except Exception as e:
        print("Exception:", str(e))
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Auth error: %s", 10000, "%s")' % (e, LASTFM_ICON))
        raise

# Scrobble tracks to Last.fm
def scrobble_track(api_key, api_secret, session_key, scrobble_data):
    params = {
        'method': 'track.scrobble',
        'api_key': api_key,
        'sk': session_key,
        'artist[0]': scrobble_data['artist'],
        'track[0]': scrobble_data['title'],
        'album[0]': scrobble_data['album'],
        'timestamp[0]': str(scrobble_data['timestamp']),
        # Do NOT include 'format' in the signature calculation, only add to POST
    }
    api_sig = generate_api_sig(params, api_secret)
    params['api_sig'] = api_sig
    params['format'] = 'json'  # Add after api_sig
    for k in params:
        if isinstance(params[k], unicode):
            params[k] = params[k].encode('utf-8')
    data = urllib.urlencode(params)
    url = "https://ws.audioscrobbler.com/2.0/"
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    return result

# Scrobble tracks to Last.fm
def scrobble_track_librefm(api_key, api_secret, session_key, scrobble_data):
    params = {
        'method': 'track.scrobble',
        'api_key': api_key,
        'sk': session_key,
        'artist[0]': scrobble_data['artist'],
        'track[0]': scrobble_data['title'],
        'album[0]': scrobble_data['album'],
        'timestamp[0]': str(scrobble_data['timestamp']),
        # Do NOT include 'format' in the signature calculation, only add to POST
    }
    api_sig = generate_api_sig(params, api_secret)
    params['api_sig'] = api_sig
    params['format'] = 'json'  # Add after api_sig
    for k in params:
        if isinstance(params[k], unicode):
            params[k] = params[k].encode('utf-8')
    data = urllib.urlencode(params)
    url = "https://libre.fm/2.0/"
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    return result

def scrobble_track_maloja(api_key, scrobble_data, api_url):
    # Build the scrobble parameters as for Last.fm
    params = {
        'method': 'track.scrobble',
        'api_key': api_key,
        'artist[0]': scrobble_data['artist'],
        'track[0]': scrobble_data['title'],
        'album[0]': scrobble_data['album'],
        'timestamp[0]': str(scrobble_data['timestamp']),
        'username': 'user',            # Maloja ignores this, but it's required by the API
        'password': api_key,           # API key goes here!
        'format': 'json'
    }
    data = urllib.urlencode(params)
    req = urllib2.Request(api_url, data)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    return result

# Scrobble tracks to ListenBrainz
def scrobble_track_listenbrainz(user_token, scrobble_data):
    url = "https://api.listenbrainz.org/1/submit-listens"
    headers = {
        "Authorization": "Token %s" % user_token,
        "Content-Type": "application/json"
    }
    payload = {
        "listen_type": "single",
        "payload": [{
            "track_metadata": {
                "artist_name": scrobble_data['artist'],
                "track_name": scrobble_data['title'],
                "release_name": scrobble_data['album']
            },
            "listened_at": scrobble_data['timestamp']
        }]
    }
    req = urllib2.Request(url, json.dumps(payload), headers)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    return result

# Parse scrobbler.log files for upload to Last.fm
def parse_scrobbler_log(log_path):
    scrobbles = []
    with open(log_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            try:
                artist, album, title, track_number, duration, rating, timestamp = line.strip().split('\t')
                scrobbles.append({
                    'artist': artist,
                    'title': title,
                    'album': album,
                    'timestamp': int(timestamp)
                })
            except Exception as e:
                print("Failed to parse line:", line)
    return scrobbles

# Remove tracks from scrobbled scrobbler.log files
def mark_scrobbles_uploaded(log_path, uploaded_count):
    # This function removes uploaded lines from the log. Only keeps header and un-uploaded lines.
    with open(log_path, 'r') as f:
        lines = f.readlines()
    header = [line for line in lines if line.startswith("#")]
    unscrobbled = lines[len(header) + uploaded_count:]
    with open(log_path, 'w') as f:
        for line in header:
            f.write(line)
        for line in unscrobbled:
            f.write(line)

# Upload scrobbles to Last.fm if requested
if lastfm_upload and not lastfm_upload_listening and lastfm_api_key and lastfm_api_secret and lastfm_username and lastfm_password:
    try:
        session_key = get_session_key(lastfm_api_key, lastfm_api_secret, lastfm_username, lastfm_password)
        scrobbles = parse_scrobbler_log(log_file_path)
        uploaded = 0
        for scrobble in scrobbles:
            try:
                result = scrobble_track(lastfm_api_key, lastfm_api_secret, session_key, scrobble)
                uploaded += 1
            except Exception as e:
                print("Failed to scrobble: %s - %s (%s): %s" % (scrobble['artist'], scrobble['title'], scrobble['album'], e))
        if uploaded > 0:
            mark_scrobbles_uploaded(log_file_path, uploaded)
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Uploaded %d scrobbles to Last.fm", 5000, "%s")' % (uploaded, LASTFM_ICON))
    except Exception as e:
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Last.fm upload failed: %s", 5000, "%s")' % (e, LASTFM_ICON))

# Upload scrobbles to Libre.fm if requested (deprecated)
if librefm_upload and not librefm_upload_listening and librefm_api_key and librefm_api_secret and librefm_username and librefm_password:
    try:
        session_key = get_session_key_librefm(librefm_api_key, librefm_api_secret, librefm_username, librefm_password)
        scrobbles = parse_scrobbler_log(log_file_path)
        uploaded = 0
        for scrobble in scrobbles:
            try:
                result = scrobble_track_librefm(librefm_api_key, librefm_api_secret, session_key, scrobble)
                uploaded += 1
            except Exception as e:
                print("Failed to scrobble: %s - %s (%s): %s" % (scrobble['artist'], scrobble['title'], scrobble['album'], e))
        if uploaded > 0:
            mark_scrobbles_uploaded(log_file_path, uploaded)
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Uploaded %d scrobbles to Libre.fm", 5000, "%s")' % (uploaded, LIBREFM_ICON))
    except Exception as e:
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Libre.fm upload failed: %s", 5000, "%s")' % (e, LIBREFM_ICON))

# Upload scrobbles to ListenBrainz if requested
if listenbrainz_upload and not listenbrainz_upload_listening and listenbrainz_user_token:
    try:
        scrobbles = parse_scrobbler_log(log_file_path)
        uploaded = 0
        for scrobble in scrobbles:
            try:
                result = scrobble_track_listenbrainz(listenbrainz_user_token, scrobble)
                uploaded += 1
            except Exception as e:
                print("Failed to scrobble: %s - %s (%s): %s" % (scrobble['artist'], scrobble['title'], scrobble['album'], e))
        if uploaded > 0:
            mark_scrobbles_uploaded(log_file_path, uploaded)
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Uploaded %d scrobbles to ListenBrainz", 5000, "%s")' % (uploaded, LISTENBRAINZ_ICON))
    except Exception as e:
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "ListenBrainz upload failed: %s", 5000, "%s")' % (e, LISTENBRAINZ_ICON))

# Upload scrobbles to Maloja if requested
if maloja_upload and maloja_api_key and maloja_api_url:
    try:
        scrobbles = parse_scrobbler_log(log_file_path)
        uploaded = 0
        for scrobble in scrobbles:
            try:
                result = scrobble_track_maloja(maloja_api_key, scrobble, maloja_api_url)
                uploaded += 1
            except Exception as e:
                print("Failed to scrobble to Maloja: %s - %s (%s): %s" % (
                    scrobble['artist'], scrobble['title'], scrobble['album'], e))
        if uploaded > 0:
            mark_scrobbles_uploaded(log_file_path, uploaded)
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Uploaded %d scrobbles to Maloja", 5000, "%s")' % (uploaded, ICON_PATH))
    except Exception as e:
        xbmc.executebuiltin('XBMC.Notification("ScrobbleBox", "Maloja upload failed: %s", 5000, "%s")' % (e, ICON_PATH))

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

            timestamp = int(time.time())
            rating = "L"

            if current_song and current_artist and current_album and duration > 30:
                song_key = (current_song, current_artist, current_album, track_number)
                if (track_pos >= duration // 2 or track_pos >= 240):
                    if last_song != song_key:
                        scrobble_data = {
                            'artist': current_artist,
                            'title': current_song,
                            'album': current_album,
                            'timestamp': timestamp
                        }
                        uploaded = False

                        # Last.fm scrobble
                        if lastfm_upload_listening and lastfm_session_key:
                            try:
                                result = scrobble_track(
                                    lastfm_api_key, lastfm_api_secret, lastfm_session_key, scrobble_data)
                                show_notification("Logged to Last.fm: %s - %s (%s)" % (
                                    current_artist, current_song, current_album), LASTFM_ICON)
                                uploaded = True
                            except Exception as e:
                                print("Immediate upload to Last.fm failed: %s" % e)
                                show_notification("Logging to Last.fm failed: %s" % e)

                        # Libre.fm scrobble
                        if librefm_upload_listening and librefm_session_key:
                            try:
                                result = scrobble_track_librefm(
                                    librefm_api_key, librefm_api_secret, librefm_session_key, scrobble_data)
                                show_notification("Logged to Libre.fm: %s - %s (%s)" % (
                                    current_artist, current_song, current_album), LIBREFM_ICON)
                                uploaded = True
                            except Exception as e:
                                print("Immediate upload to Libre.fm failed: %s" % e)
                                show_notification("Logging to Libre.fm failed: %s" % e)

                        # ListenBrainz scrobble
                        if listenbrainz_upload_listening and listenbrainz_session_key:
                            try:
                                result = scrobble_track_listenbrainz(
                                    listenbrainz_session_key, scrobble_data)
                                show_notification("Logged to ListenBrainz: %s - %s (%s)" % (
                                    current_artist, current_song, current_album), LISTENBRAINZ_ICON)
                                uploaded = True
                            except Exception as e:
                                print("Immediate upload to ListenBrainz failed: %s" % e)
                                show_notification("Logging to ListenBrainz failed: %s" % e)

                        # If not scrobbling to the above sites, scrobble offline.
                        if not uploaded:
                            write_scrobble_log(
                                current_song, current_artist, current_album,
                                track_number, duration, rating, timestamp)
                            show_notification("Logged: %s - %s (%s)" % (
                                current_artist, current_song, current_album), ICON_PATH)

                        last_song = song_key
        time.sleep(5)

# Start monitoring
if lastfm_upload_listening and lastfm_api_key and lastfm_api_secret and lastfm_username and lastfm_password:
    try:
        lastfm_session_key = get_session_key(lastfm_api_key, lastfm_api_secret, lastfm_username, lastfm_password)
    except Exception as e:
        show_notification("Last.fm auth failed: %s" % e)
        lastfm_session_key = None

if librefm_upload_listening and librefm_api_key and librefm_api_secret and librefm_username and librefm_password:
    try:
        librefm_session_key = get_session_key(librefm_api_key, librefm_api_secret, librefm_username, librefm_password)
    except Exception as e:
        show_notification("Libre.fm auth failed: %s" % e)
        librefm_session_key = None
else:
    librefm_session_key = None

if listenbrainz_upload_listening and listenbrainz_user_token:
    listenbrainz_session_key = listenbrainz_user_token  # For compatibility in monitor_music
else:
    listenbrainz_session_key = None

if maloja_upload_listening and maloja_api_key and maloja_api_url:
    try:
        result = scrobble_track_maloja(maloja_api_key, scrobble_data, maloja_api_url)
        show_notification("Logged to Maloja: %s - %s (%s)" % (
            current_artist, current_song, current_album), MALOJA_ICON)
        uploaded = True
    except Exception as e:
        print("Immediate upload to Maloja failed: %s" % e)
        show_notification("Logging to Maloja failed: %s" % e)

monitor_music()
