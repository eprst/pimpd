This a python 2.x script for conrolling MPD daemon using a Paspberry Pi with Adafruit 128x64 OLED
[bonnet](https://www.adafruit.com/product/3531).

# Installing
- start by following https://learn.adafruit.com/adafruit-128x64-oled-bonnet-for-raspberry-pi/usage
- install [python-mpd2](https://github.com/Mic92/python-mpd2/): `pip install python-mpd2`
- ~~If you want to use [snapcast](https://github.com/badaix/snapcast) volume manager: `pip install snapcast`~~

# Configuring
Edit `pimpd/pimpd.py` to your liking, all configuration options are at the top. There are also some tweakable parameters
at the top of `pimpd/screens/main.py`

# Using
Keyboard layout:
- A: load and play hard-coded playlist. Playlist name is set using `A_PLAYLIST` variable in `pimpd/screens/main.py`
- B: play next track
- joystick left/right: change volume
- joystick up/down: select playlist, center to replace current queue and start playing
- joystick center: toggle pause

# Starting as a service
Assuming repository was cloned to `/home/pi/pimpd`:

```bash
sudo cp pimpd.service /etc/systemd/system
sudo service pimpd start
sudo systemctl enable pimpd
```

# Developing
I'm using virtualenv only for developing on my laptop, was unable to make it work on Pi so far. Run `make` and
IntelliJ should correctly detect some of the libraries used, except for `Adafruit_SSD1306`.
