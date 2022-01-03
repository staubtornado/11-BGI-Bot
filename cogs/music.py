"""
Copyright (c) 2019 Valentin B.
A simple music bot written in discord.py using youtube-dl.
Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.
Requirements:
Python 3.5+
pip install -U discord.py pynacl youtube-dl
You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
------------------------------------------------------------------------------------------------------------------------
Forked by Ixyk-Wolf adding Spotify support.
For easy text based tokens, create the ones you see at line 33. Make sure your current directory is where all of the
files are.
If you do not have those, please register an application at 'https://developer.spotify.com'
The only code for spotify support is in the play command where it checks if it is a Spotify link or URI.
Changelog:
Just fixed the entire bot
Next up:
Custom animated emojis for things like processing.
More code fixes.
Spotify search.
------------------------------------------------------------------------------------------------------------------------
KNOWN BUGS:
Returning wrong Spotify track names and artists from everything.
"""

import asyncio
import functools
import itertools
import math

import random

import pyyoutube

import discord
from discord.ext.commands.cooldowns import BucketType
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import psutil

import datetime
from millify import millify
import os

youtube_dl.utils.bug_reports_message = lambda: ''

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'],
                                                           client_secret=os.environ['SPOTIFY_CLIENT_SECRET']))


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


def get_current_memory_usage():
    with open('/proc/self/status') as f:
        memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
        memusage = int(memusage)
        return memusage / 1024


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


class Spotify():
    def getTrackID(self, track):
        track = sp.track(track)
        return track["id"]

    def getPlaylistTrackIDs(self, playlist_id):
        ids = []
        playlist = sp.playlist(playlist_id)
        for item in playlist['tracks']['items']:
            track = item['track']
            ids.append(track['id'])
        return ids

    def getAlbum(self, album_id):
        album = sp.album_tracks(album_id)
        ids = []
        for item in album['items']:
            ids.append(item["id"])
        return ids

    def getTrackFeatures(self, id):
        meta = sp.track(id)
        features = sp.audio_features(id)
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']
        return f"{name} - {artist}"

    def getalbumID(self, id):
        return sp.album(id)

    def getArtistTopSongs(self, id):
        return sp.artist_top_tracks(id, country='US')

    def getArtist(self, id):
        return sp.artist(id)['name']


yt_api = pyyoutube.Api(api_key=os.environ['YOUTUBE_API_KEY'])


class YouTubeAPI():
    def getPlaylistItems(self, id):
        return yt_api.get_playlist_items(playlist_id=id, count=None)

    def getVideoInformation(self, id):
        return yt_api.get_video_by_id(video_id=id)


class YTDLSource(discord.PCMVolumeTransformer):
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
        'quiet': False,
        'no_warnings': False,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
        'username': 'julantest@gmail.com',
        'password': '123spitzhacke',
        'cookiefile': 'youtube.com_cookies.txt'
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** von **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(self, cls, ctx, search: str, *, loop: asyncio.BaseEventLoop = None):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        cls.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(cls.ytdl.extract_info, cls.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        cls.search = {"title": f'Search results for:\n**{search}**', "type": 'rich', "color": 7506394,
                      "author": {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar.url}',
                                 'icon_url': f'{ctx.author.avatar.url}'}}

        lst = []

        for e in info['entries']:
            # lst.append(f'`{info["entries"].index(e) + 1}.` {e.get("title")} **[{YTDLSource.parse_duration(int(e.get("duration")))}]**\n')
            VId = e.get('id')
            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
            lst.append(f'`{info["entries"].index(e) + 1}.` [{e.get("title")}]({VUrl})\n')

        lst.append('\n**Type a number to make a choice, Type `cancel` to exit**')
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em, delete_after=45.0)

        def check(msg):
            return msg.content.isdigit() == True and msg.channel == channel or msg.content == 'cancel' or msg.content == 'Cancel'

        try:
            m = await self.bot.wait_for('message', check=check, timeout=45.0)

        except asyncio.TimeoutError:
            rtrn = 'timeout'

        else:
            if m.content.isdigit():
                sel = int(m.content)
                if 0 < sel <= 10:
                    for key, value in info.items():
                        if key == 'entries':
                            """data = value[sel - 1]"""
                            VId = value[sel - 1]['id']
                            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
                            partial = functools.partial(cls.ytdl.extract_info, VUrl, download=False)
                            data = await loop.run_in_executor(None, partial)
                    rtrn = cls(ctx, discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data=data)
                else:
                    rtrn = 'sel_invalid'
            elif m.content == 'cancel':
                rtrn = 'cancel'
            else:
                rtrn = 'sel_invalid'

        return rtrn

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)

            duration = []
            if days > 0:
                duration.append('{}'.format(days))
            if hours > 0:
                duration.append('{}'.format(hours))
            if minutes > 0:
                duration.append('{}'.format(minutes))
            if seconds > 0:
                duration.append('{}'.format('%02d' % seconds))

            value = ':'.join(duration)

        elif duration == 0:
            value = "LIVE"

        return value


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        prefixes = [' Tsd.', ' Mio.', ' Mrd.', ' Bio.', ' Brd.']

        date = str(self.source.upload_date)
        year = date[6:]
        month = date[3:][:-5]
        day = date[:-8]

        embed = (discord.Embed(title=f'🎶 {self.source.title}',
                               description=f'[Song]({self.source.url}) | [{self.source.uploader}]({self.source.uploader_url}) | {self.source.duration} | {self.requester.mention}',
                               color=0xef2811)
                 .add_field(name='Aufrufe', value=millify(int(self.source.views), precision=2, prefixes=prefixes),
                            inline=True)
                 .add_field(name='Likes',
                            value=f'{millify(int(self.source.likes), precision=2, prefixes=prefixes)}',
                            inline=True)
                 .add_field(name='Hochgeladen',
                            value=f'<t:{str(datetime.datetime(int(year), int(month), int(day), 0, 0).timestamp())[:-2]}:R>',
                            inline=True)
                 .set_thumbnail(url=self.source.thumbnail)
                 .set_footer(text=f'{round(psutil.virtual_memory().used / (1024.0 ** 2))}MB / {round(psutil.virtual_memory().total / (1024.0 ** 2))}MB')
                 )

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True

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
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed())

            # If the song is looped
            elif self.loop:
                self.now = discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Musik(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx):
        ctx.voice_state = self.get_voice_state(ctx)

    # async def cog_command_error(self, ctx, error: commands.CommandError):
    #     await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('Du bist entweder nicht in einem Voicechannel, oder hast keinen Voicechannel angegeben.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.guild.change_voice_state(channel=destination, self_mute=False, self_deaf=True)

    @commands.command(name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Du befindest dich nicht in einem Voicechannel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx, *, volume: int):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Es wird aktuell nichts gespielt.')

        if 0 > volume > 100:
            return await ctx.send('Die Lautstärke muss zwischen 0 und 100 liegen.')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx):
        """Displays the currently playing song."""
        embed = ctx.voice_state.current.create_embed()
        await ctx.send(embed=embed)

    @commands.command(name='pause', aliases=['pa'])
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx):
        """Pauses the currently playing song."""
        print(">>>Pause Command:")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume', aliases=['re', 'res'])
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip', aliases=['s'])
    async def _skip(self, ctx):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Es wird aktuell keine Musik gespielt.')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skipvote wurde hinzugefügt: **{}/3**'.format(total_votes))

        else:
            await ctx.send('Du hast bereits gevoted.')

    @commands.command(name='forceskip', aliases=['fs', 'fskip'])
    @commands.has_permissions(manage_messages=True)
    async def _forceskip(self, ctx):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Es wird aktuell keine Musik gespielt.')
        else:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

    @commands.command(name='queue')
    async def _queue(self, ctx, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Die Wiedergabeliste ist leer.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} Songs:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Seite {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Die Wiedergabeliste ist leer.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Die Wiedergabeliste ist leer.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Es wird aktuell nichts gespielt.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play', aliases=['p'])
    @commands.cooldown(1, 15, type=BucketType.guild)
    async def _play(self, ctx, *, search: str):

        if len(ctx.voice_state.songs) > 120 or psutil.virtual_memory().percent > 75:
            return await ctx.send(embed=discord.Embed(title='Hohe Auslastung...',
                                                      description=f'In der Warteschlange befinden sich {len(ctx.voice_state.songs)}. Es können maximal 120 Songs in die Warteschlange aufgenommen werden.',
                                                      colour=0xFF0000).set_footer(
                text=f'{round(psutil.virtual_memory().used / (1024.0 ** 2))}MB / {round(psutil.virtual_memory().total / (1024.0 ** 2))}MB'))

        # Checks if song is on spotify and then searches.
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        if "https://open.spotify.com/playlist/" in search or "spotify:playlist:" in search:
            async with ctx.typing():
                try:
                    trackcount = 0
                    process = await ctx.send(
                        embed=discord.Embed(description='<a:loading:820216894703009842> Playlist wird untersucht...',
                                            colour=0x1db954)
                            .set_author(name='Spotify®',
                                        icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))
                    ids = Spotify.getPlaylistTrackIDs(self, search)

                    if len(ids) > 120 or len(ids) + len(ctx.voice_state.songs) > 120:
                        return await process.edit(embed=discord.Embed(title='Hohe Auslastung...',
                                                                      description=f'In der Warteschlange befinden sich `{len(ctx.voice_state.songs)}` Songs. Es können maximal `120 Songs` in die Warteschlange aufgenommen werden.',
                                                                      colour=0x1db954)
                                                  .set_footer(
                            text=f'{round(psutil.virtual_memory().used / (1024.0 ** 2))}MB / {round(psutil.virtual_memory().total / (1024.0 ** 2))}MB')
                                                  .set_author(name='Spotify®',
                                                              icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))

                    tracks = []
                    for i in range(len(ids)):
                        track = Spotify.getTrackFeatures(self, ids[i])
                        tracks.append(track)
                    for track in tracks:
                        trackcount += 1

                        source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)

                        song = Song(source)
                        await ctx.voice_state.songs.put(song)

                    await process.edit(embed=discord.Embed(
                        description=f':white_check_mark: `{trackcount}` Songs wurden hinzugefügt...',
                        colour=0x1db954)
                                       .set_author(name='Spotify®',
                                                   icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))

                except Exception as err:
                    await process.edit(embed=discord.Embed(title='Fehler...',
                                                           description='Ein Fehler ist beim Hinzufügen der Playlist aufgetreten.',
                                                           colour=0x1db954)
                                       .set_author(name='Spotify',
                                                   icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676')
                                       .add_field(name='Details', value=err))

        elif "https://open.spotify.com/album/" in search or "spotify:album:" in search:
            async with ctx.typing():
                process = await ctx.send(
                    embed=discord.Embed(description='<a:loading:820216894703009842> Album wird untersucht...',
                                        colour=0x1db954)
                        .set_author(name='Spotify®',
                                    icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))
                try:
                    ids = Spotify.getAlbum(self, search)
                    tracks = []

                    if len(ids) > 120 or len(ids) + len(ctx.voice_state.songs) > 120:
                        return await process.edit(embed=discord.Embed(title='Hohe Auslastung...',
                                                                      description=f'In der Warteschlange befinden sich `{len(ctx.voice_state.songs)}` Songs. Es können maximal `120` Songs in die Warteschlange aufgenommen werden.',
                                                                      colour=0x1db954)
                                                  .set_footer(
                            text=f'{round(psutil.virtual_memory().used / (1024.0 ** 2))}MB / {round(psutil.virtual_memory().total / (1024.0 ** 2))}MB')
                                                  .set_author(name='Spotify®',
                                                              icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))

                    for i in range(len(ids)):
                        track = Spotify.getTrackFeatures(self, ids[i])
                        tracks.append(track)

                    for track in tracks:
                        source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)

                        song = Song(source)
                        await ctx.voice_state.songs.put(song)

                    await process.edit(embed=discord.Embed(
                        description=f':white_check_mark: `{len(tracks)}` Songs wurden hinzugefügt...',
                        colour=0x1db954)
                                       .set_author(name='Spotify®',
                                                   icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))

                except Exception as err:
                    await process.edit(embed=discord.Embed(title='Fehler...',
                                                           description='Ein Fehler ist beim Hinzufügen des Albums aufgetreten.',
                                                           colour=0x1db954)
                                       .set_author(name='Spotify',
                                                   icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676')
                                       .add_field(name='Details', value=err))

        elif "https://open.spotify.com/track/" in search or "spotify:track:" in search:
            async with ctx.typing():
                process = await ctx.send(
                    embed=discord.Embed(description='<a:loading:820216894703009842> Track wird untersucht...',
                                        colour=0x1db954)
                        .set_author(name='Spotify®',
                                    icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))
                try:
                    ID = Spotify.getTrackID(self, search)
                    track = Spotify.getTrackFeatures(self, ID)
                    source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await process.edit(
                        embed=discord.Embed(description=f':white_check_mark: `{track}` wurde hinzugefügt...',
                                            colour=0x1db954)
                            .set_author(name='Spotify®',
                                        icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))

                except Exception as err:
                    await process.edit(embed=discord.Embed(title='Fehler...',
                                                           description='Ein Fehler ist beim Hinzufügen des Tracks aufgetreten.',
                                                           colour=0x1db954)
                                       .set_author(name='Spotify',
                                                   icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676')
                                       .add_field(name='Details', value=err))

        elif 'https://open.spotify.com/artist/' in search or 'spotify:artist:' in search:
            async with ctx.typing():
                process = await ctx.send(
                    embed=discord.Embed(description='<a:loading:820216894703009842> Künstler wird untersucht...',
                                        colour=0x1db954)
                        .set_author(name='Spotify®',
                                    icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))
                try:
                    results = Spotify.getArtistTopSongs(self, search)
                    for result in results['tracks'][:10]:
                        trackID = result['id']
                        track = Spotify.getTrackFeatures(self, trackID)

                        source = await YTDLSource.create_source(ctx, track, loop=self.bot.loop)

                        song = Song(source)
                        await ctx.voice_state.songs.put(song)

                        await process.edit(embed=discord.Embed(
                            description=f':white_check_mark: `{len(results["tracks"][:10])}` Songs von `{Spotify.getArtist(self, search)}` wurden hinzugefügt...',
                            colour=0x1db954)
                                           .set_author(name='Spotify®',
                                                       icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676'))

                except Exception as err:
                    await process.edit(embed=discord.Embed(title='Fehler...',
                                                           description=f'Ein Fehler ist beim Hinzufügen der Top-Tracks für `{Spotify.getArtist(self, search)}` aufgetreten.',
                                                           colour=0x1db954)
                                       .set_author(name='Spotify',
                                                   icon_url='https://media.discordapp.net/attachments/797127597132742668/866246117875646474/Spotify_Icon_RGB_Green.png?width=676&height=676')
                                       .add_field(name='Details', value=err))

        elif 'https://www.youtube.com/playlist?list=' in search:
            async with ctx.typing():
                playlist_id = search[38:]

                process = await ctx.send(
                    embed=discord.Embed(description='<a:loading:820216894703009842> Playlist wird untersucht...',
                                        colour=0x1db954))

                try:
                    playlist = YouTubeAPI.getPlaylistItems(self, playlist_id)

                    for video in playlist.items:

                        video_name = YouTubeAPI.getVideoInformation(self, str(video))
                        print(video_name)


                        source = await YTDLSource.create_source(ctx, str(video.snippet.resourceId)[42:][:11],
                                                                loop=self.bot.loop)
                        song = Song(source)
                        await ctx.voice_state.songs.put(song)

                    await process.edit(embed=discord.Embed(
                        description=f':white_check_mark: `{len(playlist.items)}` Songs wurden hinzugefügt...',
                        colour=0x1db954))

                except Exception as err:
                    await process.edit(embed=discord.Embed(title='Fehler...',
                                                           description=f'Ein Fehler ist beim Hinzufügen der YouTube-Playlist aufgetreten.',
                                                           colour=0x1db954)
                                       .add_field(name='Details', value=err))

        else:
            async with ctx.typing():
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send(':white_check_mark: Hinzugefügt: {}'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('Du befindest dich nicht in einem Voicechannel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Der Bot befindet sich bereits in einem Voicechannel.')


def setup(bot):
    bot.add_cog(Musik(bot))
