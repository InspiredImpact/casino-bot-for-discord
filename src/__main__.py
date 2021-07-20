import os
import argparse

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.enums import (
    ScoreChances,
    ScoreUnicode,
)
from src.casino import (
    Casino,
    Container,
)


bot = commands.Bot(
    command_prefix='.',
    strip_after_prefix=True,
    case_insensitive=True,
    description='Simple casino bot for discord',
    intents=discord.Intents.default(),
)


@bot.event  # type: ignore
async def on_ready() -> None:
    print("I'm ready!")


@bot.command(
    name='casino',
    usage='.casino <bet> <number of games>',
    description=(
        'Casino, generates lines with sectors depending'
        'on <number of games> (last argument, default: 1).\n'
        '- <bet>: Your bet\n'
        '- <number_of_games>: (1 <= x <= 3) affects the '
        'number of lines with sectors and multiplies the bet.'
    )
)  # type: ignore
async def _casino(
        ctx: commands.Context,
        bet: int = None,  # type: ignore
        number_of_games: int = 1
) -> None:
    """
    Casino, generates lines with sectors depending
    on <number of games> (last argument, default: 1).

    :param ctx: commands.Context
    :param bet: Bet of the user, but if it is None, then the command will fail.
    :param number_of_games: (1 <= x <= 3) affects the number of lines
                            with sectors and multiplies the bet.
    :return: None
    """
    if any((bet is None, bet <= 0)):
        await ctx.send('Specify the correct bet you want to play!')

    elif not 1 <= number_of_games <= 3:
        await ctx.send('You cannot play more than three games and less than one!')

    else:
        data: Container = await Casino(number_of_games).start()
        win: bool = True if data.multiplier > 0 else False
        to_footer: str = "Emoji\tCount\tPoints\n"

        for emoji, count in data.emoji_stats.items():
            # creating emoji stats in footer
            to_footer += f"{ScoreUnicode[emoji].value}\t\t:\t" \
                         f"{count}\t:\t" \
                         f"{int(ScoreChances[emoji]) // 2}\n"

        embed: discord.Embed = discord.Embed(
            title=f'Total points: {data.total_points}. ' + (
                f'You have won `{bet * data.multiplier * number_of_games}` coins.' if win
                else f'You have lose `{bet * number_of_games}` coins.'
            ),
            description="\n".join(data.board),
            color=discord.Color.green() if win else discord.Color.red()
        ).set_footer(
            text=to_footer,
            icon_url=ctx.author.avatar_url
        ).add_field(
            name=f'For x2 odds you had to score `<= {data.required_points[1]}` '
                 f'points, and for lose `>= {data.required_points[0]}.`',
            value=f'**You got:** `{data.total_points}`'
        )
        await ctx.send(embed=embed)


if __name__ == "__main__":
    load_dotenv()  # loading env here for bot_token
    parser = argparse.ArgumentParser(
        usage='Available flags: [--mypy_debug]',
        description='Small project management'
    )  # argv parser
    parser.add_argument(
        '--mypy_debug',
        type=bool,
        default=False,
        help='Debug for all project with mypy (default: False)'
    )  # mypy check for src/*.py
    namespace = parser.parse_args()  # our parsed argv
    if namespace.mypy_debug:
        # starting mypy check
        os.system('mypy --strict --config-file ../pyproject.toml ../src/*.py')

    bot.run(os.environ.get('bot_token'))
