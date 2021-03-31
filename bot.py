from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from resource_manager import get_message, DirectoriesManager, add_user
from secondary import TOKEN, States, keyboard


"""
This is a PDF-Bot convertor, it works by next plan:

1) 
"""


bot = Bot(TOKEN)
storage = MemoryStorage()
db = Dispatcher(bot, storage=storage)

dir_manager = DirectoriesManager()


@db.message_handler(commands=['start', 'help'], state='*')
async def info(message: Message):
    """
    This method sends to user all information about using this bot (send to user message 'start' from 'messages.yaml')
    """
    await bot.send_message(message.chat.id, get_message('start'), reply_markup=keyboard([['/photos']]))


@db.message_handler(commands=['photos'], state='*')
async def photos(message: Message):
    """
    This method starts process of receiving photos. It creates new folders with name that equal user's id
    in directories resources/photos and resources/pdf. Also this method adds user calling it in the table users
    ().

    Set state 'photos'.
    """
    add_user(message.chat.id)
    dir_manager.create_dirs(message.chat.id)
    await States.photos.set()
    await bot.send_message(message.chat.id, get_message('send_photos'), reply_markup=keyboard([['To PDF', 'Cancel'],
                                                                                               ['Remove last photo']]))


@db.message_handler(content_types=['photo', 'document'], state=States.photos)
async def saver(message: Message):
    """
    This method receive photo sending by user and use method for saving this photo in directory
    resources/photos/'User's id'.
    """
    if message.photo:
        photo = message.photo.pop()
    elif message.document.file_name[-3:] in ['jpg', 'png']:
        photo = message.document
    else:
        photo = None

    if photo:
        await dir_manager.save_photo(photo, message.chat.id, message.message_id)


@db.message_handler(lambda message: message.text == 'To PDF', state=States.photos)
async def to_pdf(message: Message):
    """
    If user haven't send photos, this method sent him message about this.
    Else this bot change state to name and
    """
    if dir_manager.is_empty(message.chat.id):
        await bot.send_message(message.chat.id, get_message('empty'))
    else:
        await States.next()
        await bot.send_message(message.chat.id, get_message('send_name'), reply_markup=keyboard([['Back', 'Cancel']]))


@db.message_handler(lambda message: message.text == 'Remove last photo', state=States.photos)
async def remove_last_photo(message: Message):

    if not dir_manager.is_empty(message.chat.id):
        photo = dir_manager.remove_last_photo(message.chat.id)
        await bot.delete_message(message.chat.id, photo)
        await bot.delete_message(message.chat.id, message.message_id)


@db.message_handler(commands=['remove'], state=States.photos)
async def remove(message: Message):
    if message.reply_to_message is not None and \
            (photo := dir_manager.remove_last_photo(message.chat.id, message.reply_to_message.message_id)):
        await bot.delete_message(message.chat.id, photo)
        await bot.delete_message(message.chat.id, message.message_id)


@db.message_handler(lambda message: message.text == 'Back', state=States.name)
async def back(message: Message):
    await States.previous()
    await bot.send_message(message.chat.id, get_message('continue'), reply_markup=keyboard([['To PDF', 'Cancel'],
                                                                                            ['Remove last photo']]))


@db.message_handler(lambda message: message.text == 'Cancel', state=[States.photos, States.name])
async def cancel(message: Message, state: FSMContext):
    dir_manager.delete_dirs(message.chat.id)
    await bot.send_message(message.chat.id, get_message('cancel'), reply_markup=keyboard([['/photos']]))
    await state.finish()


@db.message_handler(content_types=['text'], state=States.name)
async def sent_pdf(message: Message, state: FSMContext):
    dir_manager.converter(message.chat.id, message.text)

    doc = dir_manager.get_pdf(message.chat.id, message.text)
    await bot.send_message(message.chat.id, get_message('get_pdf'), reply_markup=keyboard([['/photos']]))
    await bot.send_document(message.chat.id, doc)
    doc.close()

    dir_manager.delete_dirs(message.chat.id)
    await state.finish()


if __name__ == '__main__':
    try:
        dir_manager.create_dirs()
        executor.start_polling(dispatcher=db)
    except Exception as e:
        input(e)
