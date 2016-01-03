from enum import Enum
from datetime import datetime
from kivy.uix.widget import Widget
import json
from kivy.storage.jsonstore import JsonStore
import socket

# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import padding

class DataMode(Enum):
    file = 0
    encrypted = 1
    communication = 2


class LogAction(Enum):
    none = 0
    press = 1
    play = 2
    stop = 3
    move = 4
    down = 5
    up = 6
    text = 7


class KL:
    log = None

    @staticmethod
    def start(mode=None):
        KL.log = KivyLogger
        if mode is None:
            mode = []
        KL.log.set_mode(mode)


class KivyLogger:
    logs = []
    t0 = None
    base_mode = []
    socket = None
    public_key = ''
    filename = None

    @staticmethod
    def __init__():
        KivyLogger.logs = []
        KivyLogger.t0 = datetime.now()

    @staticmethod
    def __del__():
        if KivyLogger.socket is not None:
            KivyLogger.socket.close()


    @staticmethod
    def set_mode(mode):
        KivyLogger.base_mode = mode
        KivyLogger.t0 = datetime.now()
        if DataMode.file in KivyLogger.base_mode:
            KivyLogger.filename = KivyLogger.t0.strftime('%Y_%m_%d_%H_%M_%S_%f') + '.log'

        if DataMode.communication in KivyLogger.base_mode:
            KivyLogger.connect()

        if DataMode.encrypted in KivyLogger.base_mode:
            KivyLogger.get_public_key()
            if KivyLogger.file is not None:
                KivyLogger.save('public_key:' + KivyLogger.public_key)

    @staticmethod
    def connect():
        try:
            KivyLogger.socket = socket.socket()
            host = socket.gethostbyaddr('192.168.1.102')
            port = 12345
            KivyLogger.socket.connect((host[2][0], port))
        except:
            KivyLogger.base_mode.remove(DataMode.communication)
        pass

    @staticmethod
    def get_public_key():
        if DataMode.communication in KivyLogger.base_mode:
            # get from communication
            pem = KivyLogger.socket.recv(1024)
        else:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend())
            prv_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption())
            KivyLogger.file = open('encrypt/' + KivyLogger.filename + '.enc', 'w')
            KivyLogger.file.write(prv_pem + '\n')
            KivyLogger.file.close()
            pem = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)

        KivyLogger.public_key = serialization.load_pem_public_key(pem, backend=default_backend())
        pass

    @staticmethod
    def reset():
        KivyLogger.logs = []
        KivyLogger.t0 = datetime.now()

    @staticmethod
    def insert(action=LogAction.none, obj='', comment='', t=None, mode=[]):
        if t is None:
            t = datetime.now()
        data = {'time':t, 'action':action, 'obj':obj, 'comment':comment}
        KivyLogger.logs.append(data)
        print('data:', data)
        if not mode:
            mode = KivyLogger.base_mode

        data_str = KivyLogger.to_str(data)

        if DataMode.encrypted in mode:
            data_str = KivyLogger.encrypt(data_str)

        if DataMode.communication in mode:
            KivyLogger.send_data(data_str)

        if DataMode.file in mode:
            KivyLogger.save(data_str)


    @staticmethod
    def save(data_str, modes=[DataMode.file]):
        KivyLogger.file = open('data/' + KivyLogger.filename, 'a')
        KivyLogger.file.write(data_str + '\n')
        KivyLogger.file.close()
        pass

    @staticmethod
    def to_str(log):
        data = {'time': log['time'].strftime('%Y_%m_%d_%H_%M_%S_%f'),
                'action': log['action'].name,
                'obj': log['obj'],
                'comment': log['comment']}
        return str(json.dumps(data))

    @staticmethod
    def encrypt(data_str):
        if DataMode.encrypted in KivyLogger.base_mode:
            data_str = KivyLogger.public_key.encrypt(
                data_str,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None))
            return data_str
        return data_str

    @staticmethod
    def send_data(data_str):
        if DataMode.communication in KivyLogger.base_mode:
            KivyLogger.socket.send(data_str.encode())
        pass


class WidgetLogger(Widget):
    name = ''

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super(WidgetLogger, self).on_touch_down(touch)
            self.log_touch(LogAction.down, touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            super(WidgetLogger, self).on_touch_move(touch)
            #self.log_touch(LogAction.move, touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            super(WidgetLogger, self).on_touch_up(touch)
            self.log_touch(LogAction.up, touch)

    def log_touch(self, action, touch):
        if KL.log is not None:
            comment = {}
            if 'angle' in touch.profile:
                comment['angle'] = touch.a
            if 'pos' in touch.profile:
                comment['pos'] = str(touch.pos)
            if 'button' in touch.profile:
                comment['button'] = touch.button

            KL.log.insert(action=action, obj=self.name, comment=json.dumps(comment))

    def on_play(self, filename):
        KL.log.insert(action=LogAction.play, obj=self.name, comment=filename)

    def on_stop(self, filename):
        KL.log.insert(action=LogAction.stop, obj=self.name, comment=filename)
