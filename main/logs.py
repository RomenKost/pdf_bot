from datetime import datetime


class Console:
    def __init__(self, name='PDF bot'):
        self.__name = name

    def __print(self, message: str, user: str, show=True):
        if show:
            print(f'[{self.__name}, {datetime.now().strftime("%Y.%m.%d %H:%M:%S")}] {message} by {user}')

    def start(self):
        self.__print('the bot was started', 'admin')

    def start_receiving(self, user: str):
        self.__print('the process of receiving photo was started', user)

    def photo(self, user):
        self.__print('the photo was received', user)

    def cancel(self, user: str):
        self.__print('the process of receiving photo was canceled', user)

    def name(self, user):
        self.__print('the process of getting name was started', user)

    def back(self, user):
        self.__print('the process of getting name was canceled', user)

    def pdf(self, user):
        self.__print('the PDF-file was sent', user)

    def remove(self, user, last=''):
        self.__print(f'the {last} photo was removed', user)
