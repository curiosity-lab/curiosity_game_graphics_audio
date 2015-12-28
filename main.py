#!/usr/bin/kivy
import kivy
kivy.require('1.0.6')
from cg_graphics_audio import *
from kivy.app import App

class CuriosityApp(App):
    cg = None
    float_layout = None
    root = None

    def build(self):
        self.cg = CuriosityGame(self)

        self.root = CuriosityWidget()
        self.float_layout = self.root.children[0].children[1]
        for key, value in self.cg.items.items():
            self.float_layout.add_widget(value)

    def on_pause(self):
        return True

if __name__ == '__main__':
    CuriosityApp().run()

