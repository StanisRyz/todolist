from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty, StringProperty
import sqlite3
from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_string('''
<SelectableLabel>
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

class SelectableLabel(RecycleDataViewBehavior, FocusBehavior, Label):

    selected  = BooleanProperty(False)
    text = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.selected = not self.selected
            return True
        return super().on_touch_down(touch)

class ToDoApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect('todo.db', check_same_thread = False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                tags TEXT,
                completed INTEGER DEFAULT 0
                )
        ''')
        self.conn.commit()

    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        layout = BoxLayout(orientation = 'vertical', spacing = 10, padding = 10)

        self.task_input = TextInput(
            hint_text = 'Введите задачу',
            multiline = False,
            size_hint = (1, None),
            height = 50,
            background_color = (0.2, 0.2, 0.2, 1),
            foreground_color = (1, 1, 1, 1)
        )
        layout.add_widget(self.task_input)

        self.tags_input = TextInput(
            hint_text = 'Введите теги',
            multiline = False,
            size_hint = (1, None),
            height = 50,
            background_color = (0.2, 0.2, 0.2, 1),
            foreground_color = (1, 1, 1, 1)
        )
        layout.add_widget(self.tags_input)

        add_button = Button(
            text = 'Добавить задачу',
            size_hint = (1, None),
            height = 50,
            background_color = (0.3, 0.5, 0.7, 1)
        )
        add_button.bind(on_press = self.add_task)
        layout.add_widget(add_button)

        self.task_list = RecycleView(
            size_hint = (1, 1),
            bar_width = 10,
            bar_color = (0.5, 0.5, 0.5, 1)
        )

        layout_manager = RecycleBoxLayout(
            default_size = (None, 50),
            default_size_hint = (1, None),
            orientation = 'vertical',
            size_hint_y = None,
            spacing = 5,
        )
        layout_manager.bind(minimum_height = layout_manager.setter('height'))

        self.task_list.layout_manager = layout_manager
        self.task_list.add_widget(layout_manager)
        self.task_list.viewclass = SelectableLabel

        self.task_list.data = self.load_tasks()
        layout.add_widget(self.task_list)

        return layout

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        tags = self.tags_input.text.strip()
        if task_text:
            try:
                self.cursor.execute(
                    'INSERT INTO tasks (title, tags, completed) VALUES (?, ?, ?)',
                    (task_text, tags, 0)
                )
                self.conn.commit()

                self.task_input.text = ''
                self.tags_input.text = ''

                self.update_task_list()

            except sqlite3.Error as e:
                print('Ошибка базы данных:', e)

    def update_task_list(self):
        self.task_list.data = self.load_tasks()
        self.task_list.refresh_from_layout()

    def load_tasks(self):
        self.cursor.execute('SELECT title, tags FROM tasks WHERE completed = 0')
        tasks = []

        for row in self.cursor.fetchall():
            title, tags = row
            display_text = f"[b]{title}[/b]"

            if tags:
                cleaned_tags = ', '.join(tag.strip() for tag in tags.split(',') if tag.strip())
                if cleaned_tags:
                    display_text += f"\n[size=12][color=aaaaaa]Теги: {cleaned_tags}[/color][/size]"

            tasks.append({
                'text': display_text,
                'selected': False
            })

        print(f"Загружено {len(tasks)} задач из базы данных")
        return tasks

    def on_stop(self):
        self.conn.close()


if __name__ == '__main__':
    ToDoApp().run()