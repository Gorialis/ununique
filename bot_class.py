# -*- coding: utf-8 -*-

import discord
from discord.ext import commands


class Ununique(commands.Bot):
    async def on_command_error(self, ctx, error):
        # Ignore user noise
        if isinstance(error, (
            commands.CommandNotFound,
            commands.CommandOnCooldown,
            commands.DisabledCommand
        )):
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{ctx.author.mention} You don't have permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention} Bad argument: {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention} Missing required argument: {error}")
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(f"{ctx.author.mention} Too many arguments for this command.")
        else:
            await ctx.send(
                f"{ctx.author.mention} An unexpected error occurred: {type(error).__name__}: {error}"
            )
