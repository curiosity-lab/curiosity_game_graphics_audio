from enum import Enum
from datetime import datetime

class LogAction(Enum):
    press = 1
    play = 2
    stop = 3
    move = 4
    down = 5
    up = 6
    text = 7


class KivyLogger:
    logs = []
    t0 = None

    def __init__(self):
        self.logs = []
        self.t0 = datetime.now()

    def reset(self):
        self.logs = []
        self.t0 = datetime.now()

    def insert(self, action, obj, comment='', t=None, mode=[DataMode.log]):
        if t is None:
            t = datetime.now()
        data = {'time':t, 'action':action, 'obj':obj, 'comment':comment}
        self.logs.append()

    def save(self, modes=[DataMode.file]):
        data = ''

        pass

    @staticmethod
    def to_str(log):
        s = log['time'].strftime('%Y_%m_%d_%H_%M_%S_%f')
        s += '.' + log['action'].name
        s += '.' + log['obj']
        s += '.' + log['comment']
        return s


class DataMode(Enum):
    file = 0
    encrypted = 1
    communication = 2


