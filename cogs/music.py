from asyncio import get_event_loop, Queue, Event, TimeoutError
from datetime import datetime, timedelta
from functools import partial as func_partial
from itertools import islice
from json import loads
from math import ceil
from os import environ
from random import shuffle
from time import gmtime, strftime
from traceback import format_exc

from async_timeout import timeout
from discord import PCMVolumeTransformer, ApplicationContext, FFmpegPCMAudio, Embed, Bot, slash_command, VoiceChannel, \
    ClientException
from discord.ext.commands import Cog
from discord.commands.permissions import has_role
from discord.utils import get
from millify import millify
from psutil import virtual_memory
from requests import get as req_get
from spotipy import Spotify, SpotifyClientCredentials, SpotifyException
from yt_dlp import utils, YoutubeDL


utils.bug_reports_message = lambda: ''
PRODUCTION: bool = False


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


sp: Spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=environ['SPOTIFY_CLIENT_ID'],
                                                            client_secret=environ['SPOTIFY_CLIENT_SECRET']))


def get_track_name(track_id) -> str:
    meta: dict = sp.track(track_id)
    name = meta["name"]
    artist = meta["artists"][0]["name"]
    return f"{name} by {artist}"


def get_playlist_track_names(playlist_id) -> list:
    songs: list = []
    meta: dict = sp.playlist(playlist_id)
    for song in meta['tracks']['items']:
        name = song["track"]["name"]
        artist = song["track"]["artists"][0]["name"]
        songs.append(f"{name} by {artist}")
    return songs


def get_album_track_names(album_id) -> list:
    songs: list = []
    meta: dict = sp.album(album_id)
    for song in meta['tracks']['items']:
        name = song["name"]
        artist = song["artists"][0]["name"]
        songs.append(f"{name} by {artist}")
    return songs


def get_artist_top_songs(artist_id) -> list:
    songs: list = []
    meta: dict = sp.artist_top_tracks(artist_id, country='US')
    for song in meta["tracks"][:10]:
        name = song["name"]
        artist = song["artists"][0]["name"]
        songs.append(f"{name} by {artist}")
    return songs


class YTDLSource(PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': False,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: ApplicationContext, source: FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.user
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get('upload_date')
        self.upload_date = f"{date[6:8]}.{date[4:6]}.{date[0:4]}"
        self.title = data.get("title")
        self.title_limited = self.parse_limited_title(self.title)
        self.title_limited_embed = self.parse_limited_title_embed(self.title)
        self.thumbnail = data.get("thumbnail")
        self.duration = self.parse_duration(data.get("duration"))
        self.url = data.get("webpage_url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count") if data.get("like_count") is not None else -1
        self.stream_url = data.get("url")

        try:
            self.dislikes = int(
                dict(loads(req_get(f"https://returnyoutubedislikeapi.com/votes?videoId={data.get('id')}")
                           .text))["dislikes"])
        except KeyError:
            self.dislikes = -1

    def __str__(self):
        return f"**{self.title_limited}** by **{self.uploader}**"

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop=None):
        loop = loop or get_event_loop()

        partial = func_partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f"**Could not find anything** that matches `{search}`")

        if "entries" not in data:
            process_info = data
        else:
            process_info = None
            for entry in data["entries"]:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(f"**Could not find anything** that matches `{search}`.")

        webpage_url = process_info["webpage_url"]
        partial = func_partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f"**Could not fetch** `{webpage_url}`")

        if "entries" not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info["entries"].pop(0)
                except IndexError:
                    raise YTDLError(f"**Could not retrieve any matches** for `{webpage_url}`")

        if int(info["duration"]) > 1728:
            raise YTDLError("This **song is too long**! Use **/**`loop` to **loop a song**.\n👉 **Why?** Keeping "
                            "Discord bots too long in voice channels is a **TOS violation** and secondly drastically "
                            "**decreases performance** resulting in a **worse experience** for all users.")
        return cls(ctx, FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: str or None):
        if duration is None:
            return "LIVE"
        duration: int = int(duration)
        if duration > 0:
            if duration < 3600:
                value = strftime('%M:%S', gmtime(duration))
            elif 86400 > duration >= 3600:
                value = strftime('%H:%M:%S', gmtime(duration))
            else:
                value = timedelta(seconds=duration)
        else:
            value = "Error"
        return value

    @staticmethod
    def parse_limited_title(title: str):
        title = title.replace('||', '')
        if len(title) > 72:
            return f"{title[:72]}..."
        else:
            return title

    @staticmethod
    def parse_limited_title_embed(title: str):
        title = title.replace('[', '')
        title = title.replace(']', '')
        title = title.replace('||', '')

        if len(title) > 45:
            return f"{title[:43]}..."
        else:
            return title


class Song:
    __slots__ = ("source", "requester")

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    @staticmethod
    def parse_counts(count: int):
        return millify(count, precision=2)

    def create_embed(self, songs):
        description = f"[Video]({self.source.url}) | [{self.source.uploader}]({self.source.uploader_url}) | " \
                      f"{self.source.duration} | {self.requester.mention}"

        date = self.source.upload_date
        timestamp = f"<t:{str(datetime(int(date[6:]), int(date[3:-5]), int(date[:-8])).timestamp())[:-2]}:R>"

        len_songs: int = len(songs)
        queue = ""
        if len_songs == 0:
            pass
        else:
            for i, song in enumerate(songs[0:5], start=0):
                queue += f"`{i + 1}.` [{song.source.title_limited_embed}]({song.source.url} '{song.source.title}')\n"

        if len_songs > 6:
            queue += f"Use **/**`queue` to show **{len_songs - 5}** more..."

        embed = Embed(title=f"🎶 {self.source.title_limited_embed}", description=description, colour=0xFF0000) \
            .add_field(name="Views", value=self.parse_counts(self.source.views), inline=True) \
            .add_field(name="Likes / Dislikes", value=f"{self.parse_counts(self.source.likes)} **/** "
                                                      f"{self.parse_counts(self.source.dislikes)}", inline=True) \
            .add_field(name="Uploaded", value=timestamp, inline=True) \
            .set_thumbnail(url=self.source.thumbnail)
        embed.add_field(name="Queue", value=queue, inline=False) if queue != "" else None
        return embed


class SongQueue(Queue):
    _queue = None

    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot, ctx):
        self.bot = bot
        self._ctx = ctx

        self.processing = False
        self.now = None
        self.current = None
        self.voice = None
        self.next = Event()
        self.songs = SongQueue()
        self.exists = True
        self.times_looped = 0

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value
        self.times_looped = 0

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None

            if not self.loop:
                self.times_looped = 0

                try:
                    async with timeout(180):
                        self.current = await self.songs.get()
                except TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    await self._ctx.send(f"💤 **Bye**. Left {self.voice.channel.mention} due to **inactivity**.")
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed(self.songs))

            elif self.loop:
                if self.times_looped >= 50:
                    self.loop = not self.loop
                    await self.current.source.channel.send("🔂 **The loop** has been **disabled** due to "
                                                           "**inactivity**.")

                self.times_looped += 1
                self.now = FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()
        self.skip_votes.clear()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()
        self.times_looped = 0

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


async def ensure_voice_state(ctx):
    if ctx.author.voice is None:
        return "❌ **You are not** connected to a **voice** channel."

    if ctx.voice_client:
        if ctx.voice_client.channel != ctx.author.voice.channel:
            return f"🎶 I am **currently playing** in {ctx.voice_client.channel.mention}."


class Music(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: ApplicationContext):
        state = self.voice_states.get(ctx.guild_id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild_id] = state
        return state

    def cog_unload(self):
        self.check_activity.stop()
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    async def cog_before_invoke(self, ctx: ApplicationContext):
        ctx.voice_state = self.get_voice_state(ctx)

    @slash_command()
    async def join(self, ctx):
        """Joins a voice channel."""

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        destination: VoiceChannel = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.respond(f"👍 **Hello**! Joined {ctx.author.voice.channel.mention}.")
            return

        try:
            ctx.voice_state.voice = await destination.connect()
        except ClientException:
            guild_channel = get(self.bot.voice_clients, guild=ctx.guild)
            if guild_channel == destination:
                pass
            else:
                await guild_channel.disconnect(force=True)
                ctx.voice_state.voice = await destination.connect()
        await ctx.respond(f"👍 **Hello**! Joined {ctx.author.voice.channel.mention}.")

    @slash_command()
    async def clear(self, ctx):
        """Clears the whole queue."""
        await ctx.defer()

        if ctx.voice_state.processing is False:
            if len(ctx.voice_state.songs) == 0:
                await ctx.respond('❌ The **queue** is **empty**.')
                return
            ctx.voice_state.songs.clear()
            await ctx.respond('🧹 **Cleared** the queue.')
        else:
            await ctx.respond('⚠ I am **currently processing** the previous **request**.')

    @slash_command()
    async def summon(self, ctx, *, channel: VoiceChannel = None):
        """Summons the bot to a voice channel. If no channel was specified, it joins your channel."""

        if not channel and not ctx.author.voice:
            return await ctx.respond("❌ You are **not in a voice channel** and you **did not specify** a voice "
                                     "channel.")

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.guild.change_voice_state(channel=destination, self_mute=False, self_deaf=True)
        await ctx.respond(f"👍 **Hello**! Joined {destination.mention}.")

    @slash_command()
    async def leave(self, ctx):
        """Clears the queue and leaves the voice channel."""
        try:
            await ctx.voice_state.stop()
            voice_channel = get(self.bot.voice_clients, guild=ctx.guild)
            if voice_channel:
                await voice_channel.disconnect(force=True)

            await ctx.respond(f"👋 **Bye**. Left {ctx.author.voice.channel.mention}.")
        except AttributeError:
            await ctx.respond(f"⚙ I am **not connected** to a voice channel so my **voice state has been reset**.")
        del self.voice_states[ctx.guild.id]

    @slash_command()
    async def volume(self, ctx, *, volume: int):
        """Sets the volume of the current song."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if not ctx.voice_state.is_playing:
            return await ctx.respond("❌ **Nothing** is currently **playing**.")

        if not (0 < volume <= 100):
            return await ctx.respond("❌ The **volume** has to be **between 0 and 100**.")

        if volume < 50:
            emoji: str = "🔈"
        elif volume == 50:
            emoji: str = "🔉"
        else:
            emoji: str = "🔊"

        ctx.voice_state.current.source.volume = volume / 100
        await ctx.respond(f"{emoji} **Volume** of the song **set to {volume}%**.")

    @slash_command()
    async def now(self, ctx):
        """Displays the currently playing song."""
        await ctx.defer()

        try:
            await ctx.respond(embed=ctx.voice_state.current.create_embed(ctx.voice_state.songs))
        except AttributeError:
            await ctx.respond("❌ **Nothing** is currently **playing**.")

    @slash_command()
    async def pause(self, ctx):
        """Pauses the currently playing song."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            return await ctx.respond("⏯ **Paused** song, use **/**`resume` to **continue**.")
        await ctx.respond("❌ Either is the **song already paused**, or **nothing is currently **playing**.")

    @slash_command()
    async def resume(self, ctx):
        """Resumes a currently paused song."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            return await ctx.respond("⏯ **Resumed** song, use **/**`pause` to **pause**.")
        await ctx.respond("❌ Either is the **song is not paused**, or **nothing is currently **playing**.")

    @slash_command()
    async def stop(self, ctx):
        """Stops playing song and clears the queue."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if ctx.voice_state.processing is False:
            ctx.voice_state.songs.clear()

            if ctx.voice_state.is_playing:
                ctx.voice_state.voice.stop()
                ctx.voice_state.current = None
                return await ctx.respond("⏹ **Stopped** the player and **cleared** the **queue**.")
            await ctx.respond("❌ **Nothing** is currently **playing**.")
        else:
            await ctx.respond('⚠ I am **currently processing** the previous **request**.')

    @slash_command()
    async def skip(self, ctx):
        """Vote to skip a song. The requester can automatically skip."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if not ctx.voice_state.is_playing:
            return await ctx.respond("❌ **Nothing** is currently **playing**.")

        voter = ctx.author
        if voter == ctx.voice_state.current.requester:
            await ctx.respond("⏭ **Skipped** the **song directly**, cause **you** added it.")
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            required_votes: int = ceil((len(ctx.author.voice.channel.members) - 1) * (1 / 3))

            if total_votes >= required_votes:
                await ctx.respond(f"⏭ **Skipped song**, as **{total_votes}/{required_votes}** users voted.")
                ctx.voice_state.skip()
            else:
                await ctx.respond(f"🗳️ **Skip vote** added: **{total_votes}/{required_votes}**")
        else:
            await ctx.respond("❌ **Cheating** not allowed**!** You **already voted**.")

    @slash_command()
    @has_role("DJ")
    async def forceskip(self, ctx):
        """Skips a song directly."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if not ctx.voice_state.is_playing:
            return await ctx.respond(f"❌ **Nothing** is currently **playing**.")
        await ctx.respond("⏭ **Forced to skip** current song.")
        ctx.voice_state.skip()

    @slash_command()
    async def queue(self, ctx, *, page: int = 1):
        """Shows the queue. You can optionally specify the page to show. Each page contains 10 elements."""
        await ctx.defer()

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('❌ The **queue** is **empty**.')

        items_per_page = 10
        pages = ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue: str = ""
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += f"`{i + 1}`. [{song.source.title_limited_embed}]({song.source.url})\n"
        duration: int = 0
        for song in ctx.voice_state.songs:
            temp = song.source.data.get("duration")
            duration += int(temp) if temp is isinstance(temp, int) else 0

        embed = Embed(title="Queue", description=f"**Songs:** {len(ctx.voice_state.songs)}\n**Duration:** "
                                                 f"{YTDLSource.parse_duration(duration)}\n\n{queue}",
                      colour=0xFF0000)

        embed.set_footer(text=f"Page {page}/{pages}")
        await ctx.respond(embed=embed)

    @slash_command()
    async def shuffle(self, ctx):
        """Shuffles the queue."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('❌ The **queue** is **empty**.')

        ctx.voice_state.songs.shuffle()
        await ctx.respond("🔀 **Shuffled** the queue.")

    @slash_command()
    async def remove(self, ctx, index: int):
        """Removes a song from the queue at a given index."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('❌ The **queue** is **empty**.')

        def ordinal(n=index):
            if isinstance(n, float):
                n = int(n)
            return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

        try:
            ctx.voice_state.songs.remove(index - 1)
        except IndexError:
            await ctx.respond(f"❌ **No song** has the **{ordinal()} position** in queue.")
            return
        await ctx.respond(f"🗑 **Removed** the **{ordinal()} song** in queue.")

    @slash_command()
    async def loop(self, ctx):
        """Loops the currently playing song. Invoke this command again to disable loop the song."""
        await ctx.defer()

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            return await ctx.respond(instance)

        if not ctx.voice_state.is_playing:
            return await ctx.respond('❌ **Nothing** is currently **playing**.')

        ctx.voice_state.loop = not ctx.voice_state.loop

        if ctx.voice_state.loop:
            await ctx.respond("🔁 **Looped** song, use **/**`loop` to **disable** loop.")
        else:
            await ctx.respond("🔁 **Unlooped** song, use **/**`loop` to **enable** loop.")

    @slash_command()
    async def play(self, ctx, *, search: str):
        """Play a song through the bot, by searching a song with the name or by URL."""
        await ctx.defer()

        if ctx.voice_state.processing:
            await ctx.respond("⚠ I am **currently processing** the previous **request**.")
            return

        instance = await ensure_voice_state(ctx)
        if isinstance(instance, str):
            await ctx.respond(instance)
            return

        if not ctx.voice_state.voice:
            await self.join(self, ctx)

        if len(ctx.voice_state.songs) >= 100:
            await ctx.respond("🥵 **Too many** songs in queue.")
            return

        if virtual_memory().percent > 75 and PRODUCTION:
            await ctx.respond("🔥 **I am** currently **experiencing high usage**. Please try again **later**.")

        async def add_song(track_name: str):
            try:
                source = await YTDLSource.create_source(ctx, track_name, loop=self.bot.loop)
            except Exception as error:
                return error

            if not ctx.voice_state.voice:
                await self.join(ctx)

            song = Song(source)
            await ctx.voice_state.songs.put(song)
            return source

        spotify_indicators: list = ["https://open.spotify.com/playlist/", "spotify:playlist:",
                                    "https://open.spotify.com/album/", "spotify:album:",
                                    "https://open.spotify.com/track/", "spotify:track:",
                                    "https://open.spotify.com/artist/", "spotify:artist:"]

        async def process():
            if any(x in search for x in spotify_indicators):
                song_names: list = []
                errors: int = 0

                try:
                    if "playlist" in search:
                        song_names.extend(get_playlist_track_names(search))
                    elif "album" in search:
                        song_names.extend(get_album_track_names(search))
                    elif "track" in search:
                        song_names.append(get_track_name(search))
                    elif "artist" in search:
                        song_names.extend(get_artist_top_songs(search))
                    else:
                        raise SpotifyException

                except SpotifyException:
                    await ctx.respond("❌ **Invalid** or **unsupported** Spotify **link**.")
                    return

                for i, song_name in enumerate(song_names):
                    if not len(ctx.voice_state.songs) >= 100:
                        song_process = await add_song(song_name)
                        if isinstance(song_process, Exception):
                            errors += 1
                        continue
                    errors += len(song_names) - i
                    break

                info: str = song_names[0].replace(" by ", "** by **") if len(song_names) == 1 else \
                    f"{len(song_names) - errors} songs"
                await ctx.respond(f":white_check_mark: Added **{info}** from **Spotify**.")
                return

            name = await add_song(search)
            if isinstance(name, YTDLError):
                await ctx.respond(f"❌ {name}")
            elif isinstance(name, utils.GeoRestrictedError):
                await ctx.respond("🌍 This **video** is **not available in** my **country**.")
            elif isinstance(name, utils.UnavailableVideoError):
                await ctx.respond("🚫 This **video is **not available**.")
            elif isinstance(name, Exception):
                traceback = format_exc()
                print(traceback) if traceback is not None else None
                await ctx.respond(f"❌ **Error**: `{name}`")
            else:
                await ctx.respond(f':white_check_mark: Added {name}')

        ctx.voice_state.processing = True
        try:
            await process()
        except Exception as e:
            await ctx.respond(f"**A fata error has occurred**: `{e}`. **You might** execute **/**`leave` to **reset "
                              f"the voice state on** this **server**.")
        ctx.voice_state.processing = False

    @slash_command()
    async def supported_links(self, ctx):
        """Lists all supported music streaming services."""
        await ctx.respond(embed=Embed(title="Supported Links", description="All supported streaming services.",
                                      colour=0xFF0000)
                          .add_field(name="YouTube", value="✅ Tracks\n❌ Playlists\n❌ Albums\n❌ Artists\n⚠ Livestreams")
                          .add_field(name="YouTube Music", value="✅ Tracks\n❌ Playlists\n❌ Albums\n❌ Artists")
                          .add_field(name="Spotify", value="✅ Tracks\n✅ Playlists\n✅ Albums\n✅ Artists")
                          .add_field(name="Soundcloud", value="✅ Tracks\n❌ Playlists\n❌ Albums\n❌ Artists")
                          .add_field(name="Twitch", value="⚠ Livestreams")
                          .add_field(name="🐞 Troubleshooting", value="If you are experiencing issues, please execute "
                                                                     "**/**`leave`. This should fix most errors.",
                                     inline=False))


def setup(bot):
    bot.add_cog(Music(bot))
