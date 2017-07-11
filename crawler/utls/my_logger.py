
import logging
from logging import Logger


class MyLogger(Logger):
    def __init__(self, name='logger'):
        super(MyLogger, self).__init__(name)
        # self.setLevel = logging.DEBUG

        self.fh = logging.FileHandler(name if '.' in name else name+'.log')
        self.fh.setLevel(logging.DEBUG)

        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)

        self.datefmt = '%Y-%m-%d %H:%M:%S'
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', self.datefmt)
        self.fh.setFormatter(self.formatter)
        self.ch.setFormatter(self.formatter)

        self.addHandler(self.fh)
        self.addHandler(self.ch)
