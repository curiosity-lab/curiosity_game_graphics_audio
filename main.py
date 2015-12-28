#!/usr/bin/kivy
import kivy
kivy.require('1.0.6')

from glob import glob
from os import listdir
from os.path import isfile, join
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
from kivy.uix.button import Button
# FIXME this shouldn't be necessary
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image


class Picture(Scatter):
    source = StringProperty(None)
    audio = []
    current = 0

    def on_transform_with_touch(self, touch):
        if self.collide_point(*touch.pos):
            if len(self.audio) > self.current:
                self.audio[self.current].play()
                self.current += 1
                CuriosityGame.current += 1


class Animation(Scatter, Image):
    pass


class CuriosityGame():
    pictures = []
    animation = None
    current = 0

    def __init__(self):
        img_path = 'images/'
        wav_path = 'audio/'
        only_files = [f for f in listdir(img_path) if isfile(join(img_path, f))]
        self.pictures = {}
        for filename in only_files:
            try:
                name = filename[:-4]

                # load the image
                self.pictures[name] = Picture(source=img_path+filename, do_rotation=False, do_scale=False)

                # load the sounds
                self.pictures[name].audio = []
                only_wav = [f for f in listdir(wav_path) if isfile(join(wav_path, f)) and name in f]
                for wav in only_wav:
                    self.pictures[name].audio.append(SoundLoader.load(wav_path + wav))

            except Exception as e:
                Logger.exception('Pictures: Unable to load <%s>' % filename)

class PicturesApp(App):
    cg = None

    def build(self):
        self.cg = CuriosityGame()

        # the root is created in pictures.kv
        root = self.root
        for key, value in self.cg.pictures.items():
            value.bind(on_transform_with_touch=self.add_animation)
            root.add_widget(value)

    def add_animation(self, instance, value):
        if self.cg.current > 0 and self.cg.animation is None:
            self.cg.animation = Animation(source='animation/cap.png')
            self.root.add_widget(self.cg.animation)

    def on_pause(self):
        return True

if __name__ == '__main__':
    PicturesApp().run()

