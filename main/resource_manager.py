from typing import BinaryIO
from yaml import safe_load as yaml
from PDFNetPython3.PDFNetPython import PDFDoc, Convert, SDFDoc
from shutil import rmtree as rmdir
from os import listdir as ls, mkdir as mk, remove as rm
from os.path import exists as ex
from sqlite3 import connect


def get_message(key: str, language='ru', path='resources/messages.yaml') -> str:
    """
    This function get message from yaml-file (that is by path) by key and language.

    YAML-file have next structure:
    key:
        language: "Message"
    """
    with open(path, 'r', encoding='UTF-8') as file:
        try:
            message = yaml(file)[key][language]
            return message
        except Exception as e:
            print(e)


def __sql(query: str, path='resources/data.db'):
    """
    This function works with SQL-database (DB), does any queries (from SELECT to INSERT).

    :param query: SQL-query
    :param path: path to the DB
    :return result, that DB return on query 'query'
    """
    database = connect(path)
    cursor = database.cursor()

    cursor.execute(query)
    result = cursor.fetchall()
    database.commit()

    database.close()
    return result


def add_user(user_id: int):
    """
    This method adds users to the database if they aren't there.

    :param user_id: id of user
    """
    if not __sql(f'SELECT user '
                 f'FROM users '
                 f'WHERE user = {user_id}'):
        __sql(f'INSERT INTO users (user)'
              f'VALUES ({user_id})')


class DirectoriesManager:
    """
    This class includes methods that help to work with files and directories.
    """
    def __init__(self, main_dir=f'resources/'):
        """
        In this constructor initialized variables '__main_dir' and '__dirs_list'

        '__main_dir' - directory, that includes directories in the list '__dirs_list'.
        '__dirs_list' - list with directories 'photos' and 'pdf'
        """
        self.__main_dir = main_dir
        self.__dirs_list = ['photos', 'pdf']

    def __user(self, user):
        if user:
            user = f'/{user}'
        return user

    def delete_dirs(self, user=''):
        user = self.__user(user)
        for dr in self.__dirs_list:
            path = f'{self.__main_dir}{dr}{user}'
            if ex(path):
                rmdir(path)

    def create_dirs(self, user=''):
        user = self.__user(user)
        self.delete_dirs(user)

        for dr in self.__dirs_list:
            mk(f'{self.__main_dir}{dr}{user}')

    def remove_last_photo(self, user: int, message=None):
        dirs = ls(f'{self.__main_dir}{self.__dirs_list[0]}/{user}')

        if message is None:
            photo = dirs[-1]
        elif f'{message}.jpg' in dirs:
            photo = f'{message}.jpg'
        else:
            return

        rm(f'{self.__main_dir}{self.__dirs_list[0]}/{user}/{photo}')
        return int(photo[:-4])

    async def save_photo(self, photo, user: int, name: int):
        await photo.download(f'{self.__main_dir}{self.__dirs_list[0]}/{user}/{name}.jpg')

    def is_empty(self, user: int):
        return not ls(f'{self.__main_dir}{self.__dirs_list[0]}/{user}')

    def get_pdf(self, user: int, name: int) -> BinaryIO:
        return open(f'{self.__main_dir}{self.__dirs_list[1]}/{user}/{name}.pdf', 'rb')

    def converter(self, user, name):
        inputFiles = ls(f'{self.__main_dir}{self.__dirs_list[0]}/{user}')
        outputFile = f'{name}.pdf'

        pdf = PDFDoc()

        for file in sorted(inputFiles):
            Convert.ToPdf(pdf, f'{self.__main_dir}{self.__dirs_list[0]}/{user}/{file}')

        pdf.Save(f'{self.__main_dir}{self.__dirs_list[1]}/{user}/{outputFile}', SDFDoc.e_compatibility)
        pdf.Close()
