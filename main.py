from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from database import Database
from screens.main_screen import MainScreen
from screens.detail_screen import DetailScreen

Builder.load_string('''
<SelectableLabel>:
    canvas.before:
        Color:
            rgba: (0.2, 0.2, 0.2, 1) if self.selected else (0.1, 0.1, 0.1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    text_size: self.width, None
    height: self.texture_size[1] + 10
    color: (1, 1, 1, 1)
    markup: True
''')


class ToDoApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        # Инициализация базы данных
        self.db = Database()

        # Создание экранов
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main', db=self.db))
        sm.add_widget(DetailScreen(name='detail', db=self.db))

        return sm

    def on_stop(self):
        self.db.close()


if __name__ == '__main__':
    ToDoApp().run()