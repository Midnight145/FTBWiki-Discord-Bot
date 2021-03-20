from discord.ext.commands import Bot
import datetime
import discord


with open('token.txt', 'r') as token:
    TOKEN = token.read().rstrip()

GUILD_ID = 457095816771928076
BOT_PREFIX = '>'
COG_FILE = "COGS.txt"

bot = Bot(command_prefix=BOT_PREFIX)

with open("COGS.txt", "r") as cogs:
    bot.all_cogs = [i.rstrip() for i in cogs.readlines()]

bot.COG_FILE = COG_FILE
bot.TOKEN = TOKEN
bot.BOT_PREFIX = '>'
bot.current_invite = None
bot.loaded_cogs, bot.unloaded_cogs = [], []


@bot.event
async def on_ready():
    bot.guild = None

    while bot.guild is None:
        bot.guild = bot.get_guild(GUILD_ID)

    for i in bot.all_cogs:
        if i not in bot.loaded_cogs:
            bot.load_extension(i)
            bot.loaded_cogs.append(i)

    game = discord.Game("Blightfall")
    await bot.change_presence(status=discord.Status.online, activity=game)

    print("Bot is ready!")
    print("Logged in as:")
    print(bot.user)

    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M.%S"))
    print()


@bot.event
async def on_disconnect():
    print("Bot disconnected")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M.%S"))
    print()


@bot.event
async def on_connect():
    print("Bot connected")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M.%S"))
    print()


bot.run(TOKEN)
