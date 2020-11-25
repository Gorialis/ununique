# -*- coding: utf-8 -*-

import io
import math
import random

import aiohttp
import discord
from discord.ext import commands


class Fun(commands.Cog):
    """
    This is where I keep my games
    """

    # Echo/say
    @commands.command(name="echo", aliases=["say"])
    async def echo_say(self, ctx: commands.Context, *, text: commands.clean_content):
        await ctx.send(text)

    # Choose/choice
    @commands.command(name="choose", aliases=["choice"])
    async def choose(self, ctx: commands.Context, *options: commands.clean_content):
        if options:
            await ctx.send(random.choice(options))
        else:
            await ctx.send("There's nothing to choose from!")

    # Math commands
    @commands.command(name="add")
    async def math_add(self, ctx: commands.Context, one: float, two: float):
        """
        Calculate a + b
        """

        await ctx.send(f"{one + two}")

    @commands.command(name="subtract")
    async def math_subtract(self, ctx: commands.Context, one: float, two: float):
        """
        Calculate a - b
        """

        await ctx.send(f"{one - two}")

    @commands.command(name="multiply")
    async def math_multiply(self, ctx: commands.Context, one: float, two: float):
        """
        Calculate a * b
        """

        await ctx.send(f"{one * two}")

    @commands.command(name="divide")
    async def math_divide(self, ctx: commands.Context, one: float, two: float):
        """
        Calculate a / b
        """

        if two == 0.0:
            await ctx.send("division by zero")
        else:
            await ctx.send(f"{one / two}")

    # Coin flip
    @commands.command(name="coinflip", aliases=['flip'])
    async def coinflip(self, ctx: commands.Context):
        await ctx.send(random.choice(['\U0001fa99 Heads', '\U0001fa99 Tails']))

    # Dice roll
    @commands.command(name="dice", aliases=["die", "roll"])
    async def dice(self, ctx: commands.Context, *dice: str):
        """
        Roll one or many dice.
        """

        # If nothing specified just roll a 6 sided dice
        dice = dice or ('1d6',)

        outcomes = []
        for die in dice:
            if 'd' in die:
                count, dice_max = map(int, die.split('d'))
            else:
                count = 1
                dice_max = int(die)

            if count > 25:
                raise commands.BadArgument(f"{count} is way too many dice, bro")
            elif count <= 0:
                raise commands.BadArgument(f"I can't roll {count} dice, man")
            elif dice_max < 1:
                raise commands.BadArgument(f"I don't have any dice that can give me a {dice_max}")

            outcomes.append(f"\N{GAME DIE} **{', '.join(str(random.randint(1, dice_max)) for _ in range(count))}**")

        await ctx.send("\n".join(outcomes))

    # Magic 8-ball
    EIGHTBALL_RESPONSES = (
        "As I see it, yes.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "It is certain.",
        "It is decidedly so.",
        "Most likely.",
        "My reply is no.",
        "My sources say no.",
        "Outlook good.",
        "Outlook not so good.",
        "Reply hazy, try again.",
        "Signs point to yes.",
        "Very doubtful.",
        "Without a doubt.",
        "Yes - definitely.",
        "Yes.",
        "You may rely on it.",
    )

    @commands.command(name="8ball", aliases=["8-ball", "eightball"])
    async def eightball(self, ctx: commands.Context):
        """
        Shake the 8-ball to determine your fate.
        """

        await ctx.send(f"\N{BILLIARDS} {random.choice(self.EIGHTBALL_RESPONSES)}")

    # Rock paper scissors
    RPS_MOVES = ("rock", "paper", "scissors")
    RPS_MATRIX = (
        # Win/loss conditions (0 is tie, 1 is player 1 wins, 2 is player 2 wins)
        # Player 1
        # R  P  S     Player 2
        ( 0, 1, 2,),  # R
        ( 2, 0, 1,),  # P
        ( 1, 2, 0,),  # S
    )

    @commands.command(name="rps", aliases=["rock_paper_scissors", "rock-paper-scissors", "rockpaperscissors"])
    async def rock_paper_scissors(self, ctx: commands.Context, user_one: discord.User = None, user_two: discord.User = None):
        """
        Rock paper scissors.
        """

        player_one = random.randrange(len(self.RPS_MOVES))
        player_two = random.randrange(len(self.RPS_MOVES))

        # If no users are given it's the author against me.
        if user_one is None:
            conclusion = (
                "It's a tie",
                f"{ctx.author.mention} wins",
                "I win",
            )[self.RPS_MATRIX[player_two][player_one]]

            text = f"{ctx.author.mention} throws {self.RPS_MOVES[player_one]}, I throw {self.RPS_MOVES[player_two]}. {conclusion}."
        # If one user is given, it's the author against them.
        elif user_two is None:
            conclusion = (
                "It's a tie",
                f"{ctx.author.mention} wins",
                f"{user_one.mention} wins",
            )[self.RPS_MATRIX[player_two][player_one]]

            text = f"{ctx.author.mention} throws {self.RPS_MOVES[player_one]}, {user_one.mention} throws {self.RPS_MOVES[player_two]}. {conclusion}."
        # Otherwise, it's the two versus eachother.
        else:
            conclusion = (
                "It's a tie",
                f"{user_one.mention} wins",
                f"{user_two.mention} wins",
            )[self.RPS_MATRIX[player_two][player_one]]

            text = f"{user_one.mention} throws {self.RPS_MOVES[player_one]}, {user_two.mention} throws {self.RPS_MOVES[player_two]}. {conclusion}."

        await ctx.send(text)

    # Minesweeper
    MINE_SPACE = "\N{BOMB}"
    EMPTY_SPACE = "\N{WHITE LARGE SQUARE}"

    @commands.command(name="minesweeper", aliases=["mines"])
    async def minesweeper(self, ctx: commands.Context, width: int = None, height: int = None):
        """
        Generates a spoiler minesweeper board

        You used to be able to create much bigger boards, but there's now a message element cap, so you can't.
        """

        # If no size is given, use 8x8
        if width is None:
            width = 8
            height = 8
        # If only one dimension is given, use it for both dimensions
        elif height is None:
            height = width

        if width < 4 or height < 4 or (width * height) > 99:
            raise commands.BadArgument(
                f"Board size must be greater than (4, 4) and have 99 spaces or less, got ({width}, {height}) [{width * height}]"
            )

        # Calculate mine count from size
        # This gives a fixed mine count of 2 at 4x4 and a fixed count of 32 at 16x16
        # Overall this ends up producing pretty easy games, but given there's no way to determine score, it's fine.
        mine_count = round((width * height) / 8)

        # Generate the mines and then the remaining blanks
        spaces = ([self.MINE_SPACE] * mine_count) + ([self.EMPTY_SPACE] * ((width * height) - mine_count))

        # Shuffle
        random.shuffle(spaces)

        # Generate the numbers
        for index, space in enumerate(spaces):
            y, x = divmod(index, width)

            # Ignore mines
            if space == self.MINE_SPACE:
                continue

            neighboring_mines = 0

            for relative_y in range(max(0, y - 1), min(height, y + 2)):
                for relative_x in range(max(0, x - 1), min(width, x + 2)):
                    relative_index = (relative_y * width) + relative_x

                    if spaces[relative_index] == self.MINE_SPACE:
                        # Oh no! A mine!
                        neighboring_mines += 1

            # If there are neighboring mines, then label this space with the number
            if neighboring_mines:
                spaces[index] = f"{neighboring_mines}\ufe0f\u20e3"

        # Now build the text lines
        lines = []
        for index in range(0, len(spaces), width):
            lines.append('\u200b'.join(f'||{space}||' for space in spaces[index : index + width]))

        # Send the message
        await ctx.send('\n'.join(lines))

    # Dad joke
    @commands.command(name="dad_joke", aliases=["dad-joke", "dadjoke"])
    async def dad_joke(self, ctx: commands.Context):
        """
        Tell me a dad joke
        """

        headers = {
            # Courtesy header
            "User-Agent": "ununique (https://github.com/Gorialis/ununique)",
            "Accept": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            # Obligatory API usage
            async with session.get("https://icanhazdadjoke.com/", headers=headers) as response:
                data = await response.json()

        await ctx.send(data['joke'])

    # Random cat
    @commands.command(name="random_cat", aliases=["cat"])
    async def random_cat(self, ctx: commands.Context):
        """
        A random cat for you sir
        """

        headers = {
            # Courtesy header
            "User-Agent": "ununique (https://github.com/Gorialis/ununique)"
        }

        async with aiohttp.ClientSession() as session:
            # Obligatory API usage
            async with session.get("https://cataas.com/cat", headers=headers) as response:
                data = await response.read()

                file_name = ({
                    "image/jpeg": "image.jpg",
                    "image/png": "image.png",
                    "image/gif": "image.gif",
                    "image/webp": "image.webp"
                }).get(response.headers['Content-Type'], 'image.png')

        await ctx.send(file=discord.File(filename=file_name, fp=io.BytesIO(data)))

    # Minimod
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx: commands.Context, *, target: discord.Member):
        await target.kick()
        await ctx.send(f"Kicked {target.mention}")

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx: commands.Context, *, target: discord.Member):
        await target.ban()
        await ctx.send(f"Banned {target.mention}")

def setup(bot: commands.Bot):
    bot.add_cog(Fun())
