# -*- coding: utf-8 -*-

import discord
import toml
from discord.ext import commands

from bot_class import Ununique


# read config
with open('config.toml', 'r') as fp:
    config = toml.load(fp)

# set intents
intents = discord.Intents.all()
# make bot
bot = Ununique(command_prefix=config['command_prefix'], intents=intents)

# load funny magnet code
bot.load_extension('jishaku')

# load other extensions
for extension in (
    'cogs.fun',
):
    bot.load_extension(extension)

# beam me up
bot.run(config['token'])
