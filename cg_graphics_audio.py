#!/usr/bin/kivy
import kivy
kivy.require('1.0.6')

from os import listdir
from os.path import isfile, join
from os.path import join, dirname
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from functools import partial
from kivy_logger import LogAction

class Item(Scatter):
    source = StringProperty(None)
    audio = []
    text = []
    current = 0
    is_playing = False

    def on_transform_with_touch(self, touch):
        if LogAction.press.value == 1:
            pass
        if self.collide_point(*touch.pos):
            self.play()

    def play(self):
        # if still has something to play
        if len(self.audio) > self.current:
            # if not playing
            if not self.is_playing:
                self.audio[self.current].play()

    def on_play(self):
        self.is_playing = True

    def on_stop(self):
        self.is_playing = False
        self.current += 1
        CuriosityGame.current += 1

    def get_text(self):
        # if still has text
        if len(self.text) > self.current:
            return self.text[self.current][::-1]
        return None


class Animation(Scatter, Image):
    pass


class CuriosityGame:
    items = []
    animation = None
    current = 0
    the_app = None

    def __init__(self, parent_app):
        self.the_app = parent_app
        items_path = 'items/'
        only_files = [f for f in listdir(items_path) if isfile(join(items_path, f))]
        self.items = {}
        for filename in only_files:
            try:
                full_name = filename[:-4]
                name = str.split(full_name, '_')[0]
                ext = filename[-3:]
                if name not in self.items.keys():
                    self.items[name] = Item(do_rotation=False, do_scale=False)
                    self.items[name].text = []
                    self.items[name].audio = []

                # load the text
                if ext == "txt":
                    f = open(items_path + filename, 'r', encoding='utf-8')
                    self.items[name].text.append(f.read())
                    f.close()

                # load the sounds
                if ext == "wav":
                    self.items[name].audio.append(SoundLoader.load(items_path + filename))
                    self.items[name].audio[-1].bind(
                        on_play=partial(self.on_play, name))
                    self.items[name].audio[-1].bind(
                        on_stop=partial(self.on_stop, name))

                # load the image
                if ext in ['jpg', 'png', 'gif']:
                    self.items[name].source = items_path + filename

            except Exception as e:
                Logger.exception('Curiosity: Unable to load <%s>' % filename)

    def on_play(self, name, par):
        self.items[name].on_play()
        text = self.items[name].get_text()
        if text:
            self.the_app.root.cg_lbl.text = text

    def on_stop(self, name, par):
        self.items[name].on_stop()
        self.the_app.root.cg_lbl.text = ''

        if self.current > 0 and self.animation is None:
            self.animation = Animation(source='animation/cap.png')
            self.the_app.float_layout.add_widget(self.animation)


class CuriosityWidget(BoxLayout):
    cg_lbl = ObjectProperty(None)