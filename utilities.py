import re

from discord.ext import commands
import discord
import json


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

    @commands.command(aliases=["kill", "stop"])
    @commands.is_owner()
    async def die(self, context):
        await context.send("Bot shutting down...")
        self.bot.db.close()
        await self.bot.close()

    @commands.command(aliases=['rl'])
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
