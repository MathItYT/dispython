import discord
import os
import aiofiles
import aiofiles.os
import asyncio
from multiprocessing import Pool
from typing import Union
from dotenv import load_dotenv


load_dotenv()
token = os.environ.get("BOT_TOKEN")


@asyncio.coroutine
async def aiolistdir(path):
    return os.listdir(path)


class DisPython(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
    async def on_message(self, message: discord.Message):
        content = message.content
        if not (content.startswith("```py") and content.endswith("```")):
            return
        channel = message.channel
        content = content.removeprefix("```py")
        content = content.removesuffix("```")
        async with aiofiles.open("file.py", "w", encoding="utf-8") as f:
            await f.write(content)
        if self.is_manim(content):
            await self.run_manim(channel)
        elif self.is_manimgl(content):
            await self.run_manimgl(channel)
        elif self.is_matplotlib(content):
            await self.run_matplotlib(channel)
        else:
            await self.run_python(channel)
        await aiofiles.os.remove("file.py")
    
    def is_manim(self, message: str):
        return "from manim import *" in message
    
    async def run_manim(self, channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
        discord.DMChannel,
        discord.PartialMessageable,
        discord.GroupChannel
    ]):
        await self.run_cmd("timeout 2m manim file.py Main --media_dir . --output_file file.mp4", channel)
        if await aiofiles.os.path.exists("file.mp4"):
            await channel.send("Here is your Manim scene!", file=discord.File("file.mp4"))
            await aiofiles.os.remove("file.mp4")
    
    def is_manimgl(self, message: str):
        return "from manimlib import *" in message
    
    async def run_manimgl(self, channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
        discord.DMChannel,
        discord.PartialMessageable,
        discord.GroupChannel
    ]):
        await self.run_cmd("timeout 2m manimgl file.py Main --video_dir . --file_name file.mp4", channel)
        if await aiofiles.os.path.exists("file.mp4"):
            await channel.send("Here is your ManimGL scene!", file=discord.File("file.mp4"))
            await aiofiles.os.remove("file.mp4")
    
    def is_matplotlib(self, message):
        return "import matplotlib.pyplot as plt" in message
    
    async def run_matplotlib(self, channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
        discord.DMChannel,
        discord.PartialMessageable,
        discord.GroupChannel
    ]):
        await self.run_python(channel)
        for file in await aiolistdir(os.getcwd()):
            if not file.endswith(".py"):
                await channel.send("Here is your Pyplot graph!", file=discord.File(file))
                await aiofiles.os.remove(file)
    
    async def run_python(self, channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
        discord.DMChannel,
        discord.PartialMessageable,
        discord.GroupChannel
    ]):
        await self.run_cmd("timeout 2m python file.py", channel)

    async def run_cmd(self, cmd, channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
        discord.DMChannel,
        discord.PartialMessageable,
        discord.GroupChannel
    ]):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        await channel.send(f'[{cmd!r} exited with {proc.returncode}]')
        if stdout:
            await channel.send(f'{stdout.decode()}')


client = DisPython(intents=discord.Intents.all())
client.run(token)