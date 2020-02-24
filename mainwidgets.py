from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, StringProperty

import re


class HoverBehavior(Widget):

    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.register_event_type('on_hover_enter')
        self.register_event_type('on_hover_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    @property
    def inside_modal_view(self):
        parent = self.parent
        while parent and not isinstance(parent, Screen):
            if isinstance(parent, ModalView):
                return True
            parent = parent.parent

    def on_mouse_pos(self, *args):
        if isinstance(App.get_running_app().root_window.children[0], Popup)\
                and not self.inside_modal_view:
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            return
        self.hovered = inside
        if inside:
            self.dispatch('on_hover_enter')
        else:
            self.dispatch('on_hover_leave')

    def on_hover_enter(self):
        pass

    def on_hover_leave(self):
        pass


class MainLabel(Label):
    pass


class MainButton(Button, HoverBehavior):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mask = None

    def on_hover_enter(self):
        with self.canvas:
            Color(rgba=(1, 1, 1, .08))
            self.mask = Rectangle(size=self.size,
                                  pos=self.pos)

    def on_hover_leave(self):
        self.canvas.remove(self.mask)


class HeadingButton(Button, HoverBehavior):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hint = None

    def on_hover_enter(self):
        self.hint = Label(text=self.name.title(),
                          center=(self.center_x, self.y - 5))
        self.add_widget(self.hint)

    def on_hover_leave(self):
        self.remove_widget(self.hint)


class MainInput(TextInput):

    def insert_text(self, substring, from_undo=False):
        if len(self.text) + len(substring) > self.allowed_len:
            substring = substring[:self.allowed_len - len(self.text)]
        if not re.match(self.allowed_pat, substring):
            substring = ''
        return super().insert_text(substring, from_undo=from_undo)


class MainPopup(Popup):
    pass


class SelectionPopup(Popup):

    message = StringProperty()

    def __init__(self, **kwargs):
        if "message" in kwargs:
            self.message = kwargs.pop("message")
        super().__init__(**kwargs)

    def add_choice(self, text, release_dismiss=True, **kwargs):
        choice_btn = MainButton(text=text)
        self.ids.choice_box.add_widget(choice_btn)
        choice_btn.bind(**kwargs)
        if release_dismiss:
            choice_btn.bind(on_release=self.dismiss)
        return choice_btn


class MessagePopup(ModalView):

    current = None

    def __init__(self, **kwargs):
        if MessagePopup.current:
            MessagePopup.current.dismiss()
        MessagePopup.current = self
        self.message = kwargs.pop("message")
        self.dismiss_schedule = None
        self.fade = None
        self.close_schedule = None
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        pass

    def on_touch_move(self, touch):
        pass

    def on_touch_up(self, touch):
        pass

    def open(self, *largs, **kwargs):
        super().open(*largs, **kwargs)
        self.dismiss_schedule = Clock.schedule_once(self.close, 1.6)

    def close(self, *largs):
        self.fade = Animation(opacity=0, t="in_sine", duration=0.6)
        self.fade.start(self)
        self.close_schedule = Clock.schedule_once(self.dismiss, 0.6)

    def dismiss(self, *largs, **kwargs):
        MessagePopup.current = None
        if self.fade:
            self.fade.cancel(self)
        if self.close_schedule:
            self.close_schedule.cancel()
        super().dismiss(*largs, **kwargs)
