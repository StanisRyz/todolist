from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
import sqlite3
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


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
    index = None
    task_id = NumericProperty(0)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.task_id = data.get('task_id', 0)
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            main_screen = app.root.get_screen('main')
            main_screen.reset_selection()

            self.selected = True

            if self.task_id:
                app.root.current = 'detail'
                app.root.get_screen('detail').load_task(self.task_id)
            return True
        return super().on_touch_down(touch)

class MainScreen(Screen):

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        layout = BoxLayout(orientation = 'vertical', spacing = 10, padding = 10)

        self.task_input = TextInput(
            hint_text = 'Введите задачу',
            multiline = False,
            size_hint = (1, None),
            height = 50,
            background_color = (0.2, 0.2, 0.2, 1),
            foreground_color = (1, 1, 1, 1),
        )
        layout.add_widget(self.task_input)

        self.tags_input = TextInput(
            hint_text='Введите теги',
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
        )
        layout.add_widget(self.tags_input)

        add_button = Button(
            text = 'Добавить задачу',
            size_hint = (1, None),
            height = 50,
            background_color = (0.3, 0.5, 0.7, 1),
        )
        add_button.bind(on_press = self.add_task)
        layout.add_widget(add_button)

        self.task_list = RecycleView(
            size_hint = (1, 1),
            bar_width = 10,
            bar_color = (0.5, 0.5, 0.5, 1),
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

        self.add_widget(layout)

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        tags = self.tags_input.text.strip()
        if task_text:
            try:
                self.app.cursor.execute(
                    'INSERT INTO tasks (title, tags, description, attachments, completed) VALUES (?, ?, ?, ?, ?)',
                    (task_text, tags, '', '', 0)
                )
                self.app.conn.commit()

                self.task_input.text = ''
                self.tags_input.text = ''

                self.task_list.data = self.load_tasks()

            except sqlite3.Error as e:
                print('Ошибка базы данных:', e)

    def load_tasks(self):
        self.app.cursor.execute('SELECT id, title, tags FROM tasks WHERE completed = 0')
        tasks = []

        for row in self.app.cursor.fetchall():
            task_id, title, tags = row
            display_text = f"[b]{title}[/b]"

            if tags:
                cleaned_tags = ', '.join(tag.strip() for tag in tags.split(',') if tag.strip())
                if cleaned_tags:
                    display_text += f"\n[size=12][color=aaaaaa]Теги: {cleaned_tags}[/color][/size]"

            tasks.append({
                'text': display_text,
                'selected': False,
                'task_id': task_id
            })

        return tasks

    def reset_selection(self):
        for item in self.task_list.data:
            item['selected'] = False

        self.task_list.refresh_from_data()

class DetailScreen(Screen):

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.task_id = None

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.title_label = Label(
            text = 'Заголовок',
            size_hint = (1, None),
            height = 50,
            color = (1, 1, 1, 1),
            markup = True
        )
        layout.add_widget(self.title_label)

        self.tags_label = Label(
            text = 'Теги',
            size_hint = (1, None),
            height = 50,
            color = (1, 1, 1, 1),
            markup = True
        )
        layout.add_widget(self.tags_label)

        self.description_input = TextInput(
            hint_text = 'Описание задачи',
            size_hint = (1, 0.3),
            background_color = (0.2, 0.2, 0.2, 1),
            foreground_color = (1, 1, 1, 1),
        )
        self.description_input.bind(text = self.save_description)
        layout.add_widget(self.description_input)

        self.attachments_input = TextInput(
            hint_text = 'Вложения',
            size_hint = (1, 0.2),
            background_color = (0.2, 0.2, 0.2, 1),
            foreground_color = (1, 1, 1, 1),
        )
        self.attachments_input.bind(text = self.save_attachments)
        layout.add_widget(self.attachments_input)

        complete_button = Button(
            text = 'Завершить задачу',
            size_hint = (1, None),
            height = 50,
            background_color = (0.3, 0.5, 0.7, 1),
        )
        complete_button.bind(on_press = self.complete_task)
        layout.add_widget(complete_button)

        back_button = Button(
            text = 'Назад',
            size_hint = (1, None),
            height = 50,
            background_color = (0.5, 0.3, 0.3, 1),
        )
        back_button.bind(on_press = self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def load_task(self, task_id):
        self.task_id = task_id
        self.app.cursor.execute('SELECT title, tags, description, attachments FROM tasks WHERE id = ?', (task_id,))
        title, tags, description, attachments = self.app.cursor.fetchone()
        self.title_label.text = f"[b]{title}[/b]"
        self.tags_label.text = f"[size=12][color=aaaaaa]Теги: {tags or 'Нет тегов'}[/color][/size]"
        self.description_input.text = description or ''
        self.attachments_input.text = attachments or ''

    def save_description(self, instance, value):
        if self.task_id:
            try:
                self.app.cursor.execute('UPDATE tasks SET description = ? WHERE id = ?', (value, self.task_id))
                self.app.conn.commit()
            except sqlite3.Error as e:
                print('Ошибка базы данных:', e)

    def save_attachments(self, instance, value):
        if self.task_id:
            try:
                self.app.cursor.execute('UPDATE tasks SET attachments = ? WHERE id = ?', (value, self.task_id))
                self.app.conn.commit()
            except sqlite3.Error as e:
                print('Ошибка базы данных:', e)

    def complete_task(self, instance):
        if self.task_id:
            try:
                self.app.cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (self.task_id,))

                self.app.conn.commit()

                main_screen = self.app.root.get_screen('main')
                main_screen.task_list.data = main_screen.load_tasks()

                self.app.root.current = 'main'
            except sqlite3.Error as e:
                print('Ошибка базы данных:', e)

    def go_back(self, instance):
        self.app.root.current = 'main'

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
                description TEXT,
                attachments TEXT,
                completed INTEGER DEFAULT 0
                )
        ''')
        self.conn.commit()

    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        sm = ScreenManager()
        sm.add_widget(MainScreen(name = 'main', app = self))
        sm.add_widget(DetailScreen(name = 'detail', app = self))

        return sm

    def on_stop(self):
        self.conn.close()

if __name__ == '__main__':
    ToDoApp().run()