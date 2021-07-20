import random
import typing as t
from types import TracebackType
from collections import Counter
from dataclasses import dataclass

from src.enums import ScoreChances


@dataclass(frozen=True)
class Container:
    board: t.List[str]                  # board with emojis
    multiplier: int                     # multiplier, affects the bet
    emoji_stats: t.Dict[str, int]       # Statistics, shows how many times each emoji was generated in board
    total_points: int                   # The total number of points scored by the user
    required_points: t.Tuple[int, int]  # Minimum and maximum limit between win and loss for total_points


@dataclass(frozen=True)
class Bet:
    MIN: int            # Threshold for total_points, if the number is <= - mul x2
    MAX: int            # Threshold for total_points, if the number is >= - defeat
    multiplier: int     # multiplier, affects the bet


odds_type = t.Tuple[t.Tuple[int, int], ...]


class Results:
    """ Class for working with casino chances and creating objects. """
    chances: t.ClassVar[odds_type] = ((31, 25), (43, 32), (44, 35))
    # You can change the limit of wins and losses in this line.
    # The first element of the nested tuple is the limit of points (>=)
    # for lose, the second is the limit for the x2 multiplier (<=).
    # Everything within these two indicators is x1.

    __slots__ = ('_data', '_bets_number', 'total_points')

    def __init__(
            self,
            bets_number: str,
            *,
            data: t.Dict[str, int]
    ) -> None:
        """
        Results.chances: chances Tuple[defeat, mul x2], where
                        `defeat` is the amount of total_point for defeat and
                        `mul x2`, respectively, for the multiplier x2
        :param bets_number: (1 <= x <= 3) affects the number of lines
                            with sectors and multiplies the bet.
        :param data: emoji stats
        """
        self._data = data
        self._bets_number = bets_number
        self.total_points: int = 0

    async def __aenter__(self) -> 'Results':
        """ Convenient and more readable `async with` construct """
        return self

    async def __aexit__(
            self,
            exc_type: t.Optional[t.Type[BaseException]],
            exc_val: t.Optional[BaseException],
            exc_tb: t.Optional[TracebackType]
    ) -> 'Results':
        return self

    @property
    def _total_points(self) -> int:
        """ Returns the total score of the user """
        for emoji, _ in self._data.items():
            self.total_points += int(ScoreChances[emoji]) // 2

        return self.total_points

    @property
    def _emoji_stats(self) -> t.Dict[str, t.Any]:
        """"
        Returns a dictionary in which the key
        is an emoji and the value is the number
        of times the emoji has been generated.
        """
        return self._data

    @property
    def _get_bet_results(self) -> 'Bet':
        """ Returns the bet object """
        _values = iter(Results.chances[int(self._bets_number) - 1])
        determinant: t.Dict[bool, int] = {
            self.total_points >= (MAX := next(_values)): 0,
            self.total_points <= (MIN := next(_values)): 2
        }
        key: t.List[int] = (
            [determinant.pop(k) for k in list(determinant.keys()) if k]
        )
        if key:
            multiplier = key[0]
        else:
            multiplier = 1

        return Bet(
            MAX=MAX,
            MIN=MIN,
            multiplier=multiplier
        )

    def create(self, board: t.List[str]) -> 'Container':
        """ Returns Container object

        :param board: Generated "emoji board"
        :return: Container
        """
        return Container(
            board=board,
            total_points=self._total_points,
            multiplier=(bet := self._get_bet_results).multiplier,
            emoji_stats=self._emoji_stats,
            required_points=(bet.MAX, bet.MIN)
        )


class Casino:
    """ Main class for working with casino. """
    delimiter: t.ClassVar[str] = ' **|** '
    space: t.ClassVar[str] = ' '

    __slots__ = ('bets_number', 'points')

    def __init__(self, bets_number: int) -> None:
        """
        :param bets_number: (1 <= x <= 3) affects the number of lines
                            with sectors and multiplies the bet.
        """
        self.bets_number = bets_number
        self.points: t.Dict[str, int] = Counter({})  # emoji stats

    @staticmethod
    def as_emoji(word: str) -> str:
        """ Returns a string word as a discord emoji
        :param word: some word
        :return: string word as emoji
        """
        return f":{word.lower()}:"

    def create_row(self) -> str:
        """ Returns 1 slot of line (3 emojis with delimiters) """
        row: str = ""
        _sequence: t.List[str] = list(ScoreChances.__members__.keys())
        keys: t.List[str] = random.choices(
            _sequence,
            weights=[int(ScoreChances[key]) for key in _sequence],
            k=3
        )
        for score in keys:
            self.points[score] += 1
            row += self.as_emoji(score) + Casino.space

        return row

    def create_line(self) -> str:
        """ Returns line of board (3 slots with emojis and delimiters) """
        line: str = ""
        for _ in range(3):
            line += Casino.delimiter + self.create_row()

        return line

    def _get_board(self) -> t.Iterator[str]:
        """ Returns iterator (board lines) """
        for _ in range(self.bets_number):
            yield self.create_line() + Casino.delimiter

    async def start(self) -> 'Container':
        """ Returns Container with all data """
        async with Results(str(self.bets_number), data=self.points) as results:
            data = results.create(list(self._get_board()))

        return data
