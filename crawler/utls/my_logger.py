
import logging
from logging import Logger


class MyLogger(Logger):
    def __init__(self, name='logger'):
        super(MyLogger, self).__init__(name)
        # self.setLevel = logging.DEBUG

        self.fh = logging.FileHandler(name if '.' in name else name+'.out')
        self.fh.setLevel(logging.DEBUG)

        self.fh_i = logging.FileHandler('info_'+name if '.' in name else name+'.out')
        self.fh_i.setLevel(logging.INFO)

        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)

        self.datefmt = '%Y-%m-%d %H:%M:%S'
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', self.datefmt)
        self.fh.setFormatter(self.formatter)
        self.ch.setFormatter(self.formatter)
        self.fh_i.setFormatter(self.formatter)

        self.addHandler(self.fh)
        self.addHandler(self.ch)
        self.addHandler(self.fh_i)