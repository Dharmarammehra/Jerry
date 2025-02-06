import asyncio
import os
import re
import json
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.future import VideosSearch
from AviaxMusic.utils.database import is_on_off
from AviaxMusic.utils.formatters import time_to_seconds

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    return out.decode("utf-8") if out else errorz.decode("utf-8")

class YouTubeAPI:
    def init(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def details(self, link: str):
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return {
                "title": result["title"],
                "duration": result["duration"],
                "thumbnail": result["thumbnails"][0]["url"].split("?")[0],
                "video_id": result["id"]
            }

    async def search(self, query: str):
        results = VideosSearch(query, limit=1)
        for result in (await results.next())["result"]:
            return f"https://www.youtube.com/watch?v={result['id']}"

    async def download_audio(self, link: str):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return f"downloads/{info['id']}.{info['ext']}"

    async def download_video(self, link: str):
        ydl_opts = {
            "format": "best[height<=720]",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return f"downloads/{info['id']}.{info['ext']}"

    async def stream_audio(self, link: str):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "-g", "-f", "bestaudio", link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip() if stdout else None
