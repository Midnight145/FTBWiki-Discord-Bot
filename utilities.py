import re

from discord.ext import commands
import urllib
import discord
import requests
import json

from requests.exceptions import InvalidSchema


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.BOT_PREFIX = bot.BOT_PREFIX

    BOT_PREFIX = '>'

    @commands.command()
    @commands.is_owner()
    async def status(self, context, *, status=None):
        if status is None:
            await self.bot.change_presence(status=discord.Status.online, activity=None)
            await context.send("Reset status")
            return
        game = discord.Game(status)
        await self.bot.change_presence(status=discord.Status.online, activity=game)
        await context.send(f"Status changed to: {status}")

    @commands.command(aliases=["kill", "stop"], help="Kills the bot")
    @commands.is_owner()
    async def die(self, context):
        await context.send("Bot shutting down...")
        self.bot.db.close()
        await self.bot.close()

    @commands.command(help=f"Will unload a cog.\nUsage: {BOT_PREFIX}unload cogname", brief="Will unload a cog.",
                      aliases=['ul'])
    @commands.is_owner()
    async def unload(self, context, arg):
        arg = arg.lower()
        if arg not in self.bot.all_cogs:
            await context.send(f"Error: cog {arg} doesn't exist. Check spelling or capitalization.")
        if arg in self.bot.unloaded_cogs:
            await context.send(f"Cog {arg} already unloaded! Try loading it first.")
        self.bot.unload_extension(arg)
        await context.send(f"Cog {arg} successfully unloaded!")
        self.bot.loaded_cogs.remove(arg)
        self.bot.unloaded_cogs.append(arg)

    @commands.command(help=f"Will load a cog.\nUsage: {BOT_PREFIX}load cogname", brief="Will load a cog.",
                      aliases=['l'])
    @commands.is_owner()
    async def load(self, context, arg):
        arg = arg.lower()
        if arg not in self.bot.all_cogs:
            await context.send(f"Error: cog {arg} doesn't exist. Check spelling or capitalization.")
        if arg in self.bot.loaded_cogs:
            await context.send(f"Cog {arg} already loaded! Try unloading it first.")
        self.bot.load_extension(arg)
        await context.send(f"Cog {arg} successfully loaded!")
        self.bot.unloaded_cogs.remove(arg)
        self.bot.loaded_cogs.append(arg)

    @commands.command(help=f"Will reload a cog.\nUsage: {BOT_PREFIX}reload cogname", brief="Will reload a cog.",
                      aliases=['rl'])
    @commands.is_owner()
    async def reload(self, context, arg):
        arg = arg.lower()
        if arg not in self.bot.all_cogs:
            await context.send(f"Error: cog {arg} doesn't exist. Check spelling or capitalization.")
        if arg in self.bot.unloaded_cogs:
            await context.send(f"Cog {arg} is unloaded, loading instead.")
            self.bot.load_extension(arg)
            await context.send(f"Cog {arg} successfully loaded!")
            self.bot.unloaded_cogs.remove(arg)
            self.bot.loaded_cogs.append(arg)
            return
        self.bot.reload_extension(arg)
        await context.send(f"Cog {arg} successfully reloaded!")

    @commands.command(aliases=['ac'])
    @commands.is_owner()
    async def add_cog(self, context, arg):
        arg = arg.lower()
        if arg not in self.bot.all_cogs:
            self.bot.all_cogs.append(arg)
            with open(self.bot.COG_FILE, "a") as cogs:
                cogs.write("\n" + arg + "\n")
            await context.send(f"Cog {arg} successfully added!")
        else:
            await context.send(f"Cog {arg} already seems to exist, not adding.")

    @commands.command(aliases=['dc'])
    @commands.is_owner()
    async def delete_cog(self, context, arg):
        if arg in self.bot.all_cogs:
            self.bot.all_cogs.remove(arg)

            with open(self.bot.COG_FILE, "w") as cogs:
                cogs.writelines([i + "\n" for i in self.bot.all_cogs])
            await context.send(f"Cog {arg} successfully deleted!")
        else:
            await context.send(f"Cog {arg} does not exist, not deleting.")

    @commands.command()
    @commands.is_owner()
    async def rename(self, context, *, name):
        await self.bot.user.edit(username=name)
        await context.send("Username successfully changed!")

    @commands.command(aliases=["addemote", "ae"])
    @commands.has_permissions(manage_emojis=True)
    async def add_emote(self, context, name, image=None):
        if image is None:
            if context.message.attachments:
                await context.guild.create_custom_emoji(name=name, image=(await context.message.attachments[0].to_file()).fp.read())
                await context.send("Emote " + name + " added")
                return
            else:
                await context.send("Image is a require argument that is missing")
                return
        try:
            emote = requests.get(image).content
        except InvalidSchema:
            image = self.bot.get_emoji(int(list((re.search("<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>", image)).groups())[-1])).url
            emote = requests.get(image).content
        await context.guild.create_custom_emoji(name=name, image=emote)
        await context.send("Emote " + name + " added")

    @commands.command()
    async def botinfo(self, context):
        creator = await self.bot.fetch_user(self.bot.owner_id)
        embed = discord.Embed(
            title="Bot Info",
            description="Archmage Xilith, a bot made for the Unofficial Blightfall Discord Server",
            color=discord.Color.gold()
        )
        embed.set_author(name="Created by " + str(creator), icon_url=creator.avatar_url)
        embed.set_thumbnail(url=creator.avatar_url)
        embed.set_image(url=self.bot.user.avatar_url)
        embed.add_field(name="User ID", value=self.bot.user.id, inline=False)
        embed.add_field(name="Join Date",
                        value=self.bot.guild.get_member(self.bot.user.id).joined_at.strftime("%Y-%m-%d %H:%M.%S"),
                        inline=False)
        embed.add_field(name="Other Info", value="Created with discord.py", inline=False)
        await context.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if type(error) == commands.CommandNotFound:
            return
        await context.send(error)


def setup(bot):
    bot.add_cog(Utilities(bot))
