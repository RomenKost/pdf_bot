from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup

"""
This is module with secondary classes and methods.

Have one variable - TOKEN.
TOKEN: bot token
"""

TOKEN = ''


class States(StatesGroup):
    """
    This is class with all possible states of program.

    State 'photos': if this state is activated, program receives photos sending by user.
    State 'name': if this state is activate, program gets name of PDF-file.
    """
    photos = State()
    name = State()


def keyboard(buttons: list) -> ReplyKeyboardMarkup:
    """
    This is function that create keyboard using template buttons (buttons in one list in template
    will be in one row in keyboard).

    :param buttons: it's list with lists with names of buttons. Every list of buttons is the individual line.
    :return kb: keyboard
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in buttons:
        kb.add(*row)
    return kb
