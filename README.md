# ScrobbleBox - an offline Rockbox-style scrobble logger for XBMC4Xbox
A simple XBMC4Xbox addon that logs scrobbled songs to a "scrobbler.log" file, like Rockbox does. Pairs well with [rb-scrobbler](https://github.com/jeselnik/rb-scrobbler)

![1](screenshots/screenshot011.bmp)
![2](screenshots/screenshot012.bmp)

## How to use:
- Install ScrobbleBox to your scripts folder in XBMC4Xbox
- Run ScrobbleBox, select "Start ScrobbleBox", listen to music and enjoy as ScrobbleBox scrobbles in the background! (All tracks are automatically scrobbled after reaching at least the halfway point!)
- To enable/disable ScrobbleBox on startup, you can do so from the main ScrobbleBox menu!
- To upload scrobbles, grab your scrobbles from "scrobbler.log" from your Q directory and use a program such as rb-scrobbler to upload it! (uploading directly to last.fm/libre.fm is TBA)

## Bugs:
- Seeking through tracks can make duplicate log entries appear. 

## TODO:
- Allow upload to either last.fm or libre.fm (or at least to a host PC)

## Why?
Because I do a lot of my music listening on my original Xbox, as it's the main thing connected to my media center with a CD/DVD drive, so I like being able to scrobble my tracks as I listen to them. As I have an iPod that I log scrobbles onto offline, I figured I wanted to make a similar offline solution for the original Xbox, to futureproof scrobbling on XBMC4Xbox against further SSL/TLS degradation. 
