import enum
import math
import typing as t


class GeneratePercents(enum.IntEnum):

    def _generate_next_value_(  # type: ignore
            name: str,
            start: t.Optional[int],
            count: int,
            last_values: t.Optional[t.List[int]]
    ) -> t.Union[int, float]:
        """
        By changing the auto() function, generates
        percentages for the casino emojis.

        Here you can change the formula to change the odds for
        certain emoji or even set them manually in ScoreChances.

        :param name: the name of the member
        :param start: the initial start value or None
        :param count: the number of existing members
        :param last_values: the last value assigned or None
        :return: Union[int, float]
        """
        return math.ceil((count + 1 << 2) / 1.9)


class ScoreChances(GeneratePercents):
    """ Percentages for the casino emojis """
    CHERRIES = enum.auto()
    PEACH = enum.auto()
    COCONUT = enum.auto()
    KIWI = enum.auto()
    BANANA = enum.auto()
    AVOCADO = enum.auto()
    WATERMELON = enum.auto()
    STRAWBERRY = enum.auto()
    GRAPES = enum.auto()


class ScoreUnicode(enum.Enum):
    """ Unicode casino emojis """
    CHERRIES = u"\U0001f352"
    PEACH = u"\U0001f351"
    COCONUT = u"\U0001f965"
    KIWI = u"\U0001f95d"
    BANANA = u"\U0001f34c"
    AVOCADO = u"\U0001f951"
    WATERMELON = u"\U0001f349"
    STRAWBERRY = u"\U0001f353"
    GRAPES = u"\U0001f347"
