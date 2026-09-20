""" 
this is AI slop
"""
import asyncio
import hashlib
import threading

from dbus_next import Variant
from dbus_next.aio import MessageBus
from dbus_next.constants import PropertyAccess
from dbus_next.service import ServiceInterface, dbus_property, method


BUS_NAME = "org.mpris.MediaPlayer2.myplayer"
OBJECT_PATH = "/org/mpris/MediaPlayer2"


# ======================================================================
# org.mpris.MediaPlayer2
# ======================================================================

class MediaPlayer2(ServiceInterface):
    def __init__(self):
        super().__init__("org.mpris.MediaPlayer2")

    @dbus_property(access=PropertyAccess.READ)
    def Identity(self) -> "s":
        return "myplayer"

    @dbus_property(access=PropertyAccess.READ)
    def DesktopEntry(self) -> "s":
        return "myplayer"

    @dbus_property(access=PropertyAccess.READ)
    def CanQuit(self) -> "b":
        return False

    @dbus_property(access=PropertyAccess.READ)
    def CanRaise(self) -> "b":
        return False

    @dbus_property(access=PropertyAccess.READ)
    def HasTrackList(self) -> "b":
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Fullscreen(self) -> "b":
        return False

    @dbus_property(access=PropertyAccess.READ)
    def CanSetFullscreen(self) -> "b":
        return False

    @dbus_property(access=PropertyAccess.READ)
    def SupportedUriSchemes(self) -> "as":
        return ["file"]

    @dbus_property(access=PropertyAccess.READ)
    def SupportedMimeTypes(self) -> "as":
        return [
            "audio/mpeg",
            "audio/ogg",
            "audio/wav",
            "audio/flac",
        ]

    @method()
    def Raise(self):
        pass

    @method()
    def Quit(self):
        pass


# ======================================================================
# org.mpris.MediaPlayer2.Player
# ======================================================================

class MediaPlayer2Player(ServiceInterface):
    def __init__(self, player):
        super().__init__("org.mpris.MediaPlayer2.Player")

        self.player = player

        # IMPORTANT:
        # This is state owned by the MPRIS interface.
        #
        # Do NOT call player.shuffled_playlist() from the getter.
        self._shuffle = False

        self._last_playback_status = None
        self._last_volume = None
        self._last_track_id = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _playback_status(self):
        """
        Adapt this to the Player's existing semantics.

        In your Player:
            running         = program is still running
            song_is_paused  = playback is paused

        So running cannot be used as the playback status.
        """
        if not self.player.running:
            return "Stopped"

        if self.player.song_is_paused:
            return "Paused"

        return "Playing"

    def _position(self):
        """
        MPRIS Position is in microseconds.
        """
        seconds = getattr(self.player, "song_seconds", 0)
        return int(float(seconds) * 1_000_000)

    def _track_path(self):
        """
        Create a deterministic MPRIS object path for the current file.
        """
        path = self.player.playlist.current.file_path

        digest = hashlib.sha1(
            os_path_bytes(path)
        ).hexdigest()

        return f"/org/mpris/MediaPlayer2/track/{digest}"

    def _metadata(self):
        """
        Return metadata for the current song.

        Unknown fields are simply omitted.
        """
        song = self.player.playlist.current

        metadata = {
            "mpris:trackid": Variant(
                "o",
                self._track_path(),
            ),
        }

        # Your Playlist/Song implementation appears to expose name.
        name = getattr(song, "name", None)

        if name:
            metadata["xesam:title"] = Variant(
                "s",
                str(name),
            )

        # Add these automatically if your Song object has them.
        artist = getattr(song, "artist", None)
        if artist:
            metadata["xesam:artist"] = Variant(
                "as",
                [str(artist)],
            )

        album = getattr(song, "album", None)
        if album:
            metadata["xesam:album"] = Variant(
                "s",
                str(album),
            )

        length = getattr(
            self.player,
            "song_length",
            None,
        )

        if length is not None:
            metadata["mpris:length"] = Variant(
                "x",
                int(float(length) * 1_000_000),
            )

        return metadata

    def _volume(self):
        return float(self.player.volume)

    # ------------------------------------------------------------------
    # MPRIS properties
    # ------------------------------------------------------------------

    @dbus_property(access=PropertyAccess.READ)
    def PlaybackStatus(self) -> "s":
        return self._playback_status()

    @dbus_property(access=PropertyAccess.READWRITE)
    def LoopStatus(self) -> "s":
        return "None"

    @LoopStatus.setter
    def LoopStatus(self, value: "s"):
        # Looping is not implemented by Player.
        #
        # Accept the property so clients don't get UNKNOWN_PROPERTY,
        # but do not change Player behaviour.
        if value not in ("None", "Track", "Playlist"):
            raise ValueError(
                f"Invalid LoopStatus: {value}"
            )

    @dbus_property(access=PropertyAccess.READWRITE)
    def Rate(self) -> "d":
        return 1.0

    @Rate.setter
    def Rate(self, value: "d"):
        if float(value) != 1.0:
            raise ValueError(
                "Variable playback rate is not supported"
            )

    @dbus_property(access=PropertyAccess.READWRITE)
    def Shuffle(self) -> "b":
        # VERY IMPORTANT:
        #
        # Never call player.shuffled_playlist() here.
        #
        # D-Bus clients may read Shuffle whenever they issue other
        # commands. A getter must not start/change playback.
        return self._shuffle

    @Shuffle.setter
    def Shuffle(self, value: "b"):
        value = bool(value)

        if value == self._shuffle:
            return

        self._shuffle = value

        if value:
            # This is intentionally an ACTION.
            #
            # Your existing Player implementation changes the playlist
            # and starts a song. That's your intended behaviour.
            self.player.shuffled_playlist()

        self.emit_properties_changed({
            "Shuffle": self._shuffle,
        })

    @dbus_property(access=PropertyAccess.READ)
    def Metadata(self) -> "a{sv}":
        return self._metadata()

    @dbus_property(access=PropertyAccess.READWRITE)
    def Volume(self) -> "d":
        return self._volume()

    @Volume.setter
    def Volume(self, value: "d"):
        self.player.set_volume(
            value=float(value)
        )

        self.emit_properties_changed({
            "Volume": self._volume(),
        })

    @dbus_property(access=PropertyAccess.READ)
    def Position(self) -> "x":
        return self._position()

    @dbus_property(access=PropertyAccess.READ)
    def MinimumRate(self) -> "d":
        return 1.0

    @dbus_property(access=PropertyAccess.READ)
    def MaximumRate(self) -> "d":
        return 1.0

    @dbus_property(access=PropertyAccess.READ)
    def CanGoNext(self) -> "b":
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanGoPrevious(self) -> "b":
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanPlay(self) -> "b":
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanPause(self) -> "b":
        return True

    @dbus_property(access=PropertyAccess.READ)
    def CanSeek(self) -> "b":
        # Your Player supports seeking internally, but you have not
        # exposed MPRIS Seek/SetPosition yet.
        return False

    @dbus_property(access=PropertyAccess.READ)
    def CanControl(self) -> "b":
        return True

    # ------------------------------------------------------------------
    # MPRIS methods
    # ------------------------------------------------------------------

    @method()
    def Play(self):
        print("MPRIS: Play", flush=True)

        # Your existing semantics:
        # Player.play() = unpause current song.
        self.player.play()

        self._emit_playback_status()

    @method()
    def Pause(self):
        print("MPRIS: Pause", flush=True)

        # Your Player.stop() intentionally means "pause".
        self.player.stop()

        self._emit_playback_status()

    @method()
    def PlayPause(self):
        print("MPRIS: PlayPause", flush=True)

        self.player.playpause()

        self._emit_playback_status()

    @method()
    def Stop(self):
        print("MPRIS: Stop", flush=True)

        # Deliberately uses your existing semantics.
        self.player.stop()

        self._emit_playback_status()

    @method()
    def Next(self):
        print("MPRIS: Next", flush=True)

        self.player.start_next_song()

        self._emit_track_changed()

    @method()
    def Previous(self):
        print("MPRIS: Previous", flush=True)

        self.player.start_previous_song()

        self._emit_track_changed()

    # ------------------------------------------------------------------
    # Property change helpers
    # ------------------------------------------------------------------

    def _emit_playback_status(self):
        status = self._playback_status()

        if status == self._last_playback_status:
            return

        self._last_playback_status = status

        self.emit_properties_changed({
            "PlaybackStatus": status,
        })

    def _emit_track_changed(self):
        track_id = self._track_path()

        self.emit_properties_changed({
            "Metadata": self._metadata(),
            "Position": self._position(),
        })

        self._last_track_id = track_id

    def poll_changes(self):
        """
        Called periodically by the D-Bus thread.

        This catches changes made through the curses UI too, not just
        changes made through MPRIS.
        """

        try:
            # Playback state changed?
            self._emit_playback_status()

            # Volume changed?
            volume = self._volume()

            if volume != self._last_volume:
                self._last_volume = volume

                self.emit_properties_changed({
                    "Volume": volume,
                })

            # Track changed?
            track_id = self._track_path()

            if track_id != self._last_track_id:
                self._last_track_id = track_id

                self.emit_properties_changed({
                    "Metadata": self._metadata(),
                    "Position": self._position(),
                })

        except Exception as exc:
            # Don't let a transient Player error kill the D-Bus thread.
            print(
                f"MPRIS polling error: {exc}",
                flush=True,
            )


# ======================================================================
# Service startup
# ======================================================================

def mpris_dbus_start(player):
    """
    Start the MPRIS service on a background thread.

    The supplied Player object is used exactly as-is.
    """

    async def dbus_main():
        try:
            bus = await MessageBus().connect()

            print(
                f"MPRIS: connected to session bus",
                flush=True,
            )

            reply = await bus.request_name(BUS_NAME)

            print(
                f"MPRIS: request_name -> {reply}",
                flush=True,
            )

            root = MediaPlayer2()
            mpris_player = MediaPlayer2Player(player)

            bus.export(
                OBJECT_PATH,
                root,
            )

            bus.export(
                OBJECT_PATH,
                mpris_player,
            )

            # Establish initial cached values.
            mpris_player._last_playback_status = (
                mpris_player._playback_status()
            )

            mpris_player._last_volume = (
                mpris_player._volume()
            )

            mpris_player._last_track_id = (
                mpris_player._track_path()
            )

            print(
                f"MPRIS: running as {BUS_NAME}",
                flush=True,
            )

            print(
                f"MPRIS: object {OBJECT_PATH}",
                flush=True,
            )

            # Keep an eye on changes made outside D-Bus, e.g.:
            #
            #   Space
            #   <
            #   >
            #   Up/Down
            #   s
            #
            # This does not call any Player actions.
            while True:
                await asyncio.sleep(0.1)

                mpris_player.poll_changes()

        except Exception:
            import traceback

            print(
                "MPRIS: fatal D-Bus error",
                flush=True,
            )

            traceback.print_exc()

    def dbus_thread():
        asyncio.run(dbus_main())

    thread = threading.Thread(
        target=dbus_thread,
        name="mpris-dbus",
        daemon=True,
    )

    thread.start()

    return thread


# ======================================================================
# Small helper
# ======================================================================

def os_path_bytes(path):
    """
    Make a filesystem path deterministic for hashing without making
    assumptions about its encoding.
    """
    return str(path).encode("utf-8", errors="surrogatepass")
