import discord
from discord.ext import commands
from dotenv import load_dotenv
import shutil
import os
import uuid
import functools
import subprocess


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = commands.Bot("!", intents=discord.Intents.all())


async def run_blocking(blocking_func, *args, **kwargs):
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.command()
async def python(ctx: commands.Context):
    if ctx.message.reference is None:
        await ctx.send("You must reply to a Python code block!")
        return
    channel = bot.get_channel(ctx.message.reference.channel_id)
    msg = await channel.fetch_message(ctx.message.reference.message_id)
    txt = msg.content
    if not txt.startswith("```py") or not txt.endswith("```"):
        await ctx.send("The message you're replying to must be a Python code block!")
        return
    txt = txt.removeprefix("```py").removesuffix("```")
    filename = str(uuid.uuid4()) + ".py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt)
    bot_msg = None
    p = subprocess.Popen(["timeout", "120", "python", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b""):
        if bot_msg is None:
            bot_msg = await channel.send(line.decode(errors="replace"))
        else:
            bot_msg = await bot_msg.edit(content=bot_msg.content + "\n" + line.decode(errors="replace"))
    os.remove(filename)


@bot.command()
async def manim(ctx: commands.Context, arg1, arg2):
    if ctx.message.reference is None:
        await ctx.send("You must reply to a Python code block!")
        return
    channel = bot.get_channel(ctx.message.reference.channel_id)
    msg = await channel.fetch_message(ctx.message.reference.message_id)
    txt = msg.content
    if not txt.startswith("```py") or not txt.endswith("```"):
        await ctx.send("The message you're replying to must be a Python code block!")
        return
    txt = txt.removeprefix("```py").removesuffix("```")
    filename = str(uuid.uuid4()) + ".py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt)
    process = subprocess.Popen(["timeout", "120", "manim", filename, arg1, "-o", arg2], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        pass
    media_file = os.path.join("media", "videos", filename.removesuffix(".py"), "1080p60", arg2)
    if not os.path.exists(media_file):
        media_file = os.path.join("media", "images", filename.removesuffix(".py"), arg2)
    if os.path.exists(media_file):
        await ctx.send("Here is your Manim media file!", file=discord.File(media_file))
    else:
        await ctx.send("There was an error, please check your code!")
    os.remove(filename)
    shutil.rmtree("media")
    shutil.rmtree("__pycache__")


@bot.command()
async def matplotlib(ctx: commands.Context, arg):
    if ctx.message.reference is None:
        await ctx.send("You must reply to a Python code block!")
        return
    channel = bot.get_channel(ctx.message.reference.channel_id)
    msg = await channel.fetch_message(ctx.message.reference.message_id)
    txt = msg.content
    if not txt.startswith("```py") or not txt.endswith("```"):
        await ctx.send("The message you're replying to must be a Python code block!")
        return
    txt = txt.removeprefix("```py").removesuffix("```")
    filename = str(uuid.uuid4()) + ".py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt)
    bot_msg = None
    p = subprocess.Popen(["timeout", "120", "python", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b""):
        pass
    if not os.path.exists(arg):
        await channel.send("There's not any file with that name!")
    else:
        await channel.send("Here is your Matplotlib figure!", file=discord.File(arg))
    os.remove(filename)


bot.run(BOT_TOKEN)