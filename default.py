import xbmc
import xbmcgui
import xml.etree.ElementTree as ET
import sys

def main():
    dialog = xbmcgui.Dialog()
    feeds = [
        ("Start ScrobbleBox", "RunScript(Q:\\scripts\\ScrobbleBox\\scrobblebox.py)"),
        ("Stop ScrobbleBox", "StopScript(Q:\\scripts\\ScrobbleBox\\settings.py)"),
        ("Settings", "RunScript(Q:\\scripts\\ScrobbleBox\\settings.py)"),
#        ("Upload Scrobbles", "RunScript(Q:\\scripts\\ScrobbleBox\\upload.py)"),
        ("Enable/Disable On Startup", "RunScript(Q:\\scripts\\ScrobbleBox\\autoexec-scrobblebox.py)"),
    ]
    
    feed_list = [name for name, _ in feeds]
    selected = dialog.select(u"ScrobbleBox", feed_list)
    
    if selected >= 0:
        name, url = feeds[selected]
        if "RunScript" in url:
            xbmc.executebuiltin(url)

if __name__ == '__main__':
    main()
