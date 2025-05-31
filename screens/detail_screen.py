from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label


class DetailScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.task_id = None
        self._build_ui()

    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.title_label = Label(
            text='Заголовок',
            size_hint=(1, None),
            height=50,
            color=(1, 1, 1, 1),
            markup=True
        )
        layout.add_widget(self.title_label)

        self.tags_label = Label(
            text='Теги',
            size_hint=(1, None),
            height=50,
            color=(1, 1, 1, 1),
            markup=True
        )
        layout.add_widget(self.tags_label)

        self.description_input = TextInput(
            hint_text='Описание задачи',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
        )
        self.description_input.bind(text=self.save_description)
        layout.add_widget(self.description_input)

        self.attachments_input = TextInput(
            hint_text='Вложения',
            size_hint=(1, 0.2),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
        )
        self.attachments_input.bind(text=self.save_attachments)
        layout.add_widget(self.attachments_input)

        complete_button = Button(
            text='Завершить задачу',
            size_hint=(1, None),
            height=50,
            background_color=(0.3, 0.5, 0.7, 1),
        )
        complete_button.bind(on_press=self.complete_task)
        layout.add_widget(complete_button)

        back_button = Button(
            text='Назад',
            size_hint=(1, None),
            height=50,
            background_color=(0.5, 0.3, 0.3, 1),
        )
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def load_task(self, task_id):
        self.task_id = task_id
        title, tags, description, attachments = self.db.get_task_details(task_id)
        self.title_label.text = f"[b]{title}[/b]"
        self.tags_label.text = f"[size=12][color=aaaaaa]Теги: {tags or 'Нет тегов'}[/color][/size]"
        self.description_input.text = description or ''
        self.attachments_input.text = attachments or ''

    def save_description(self, instance, value):
        if self.task_id:
            self.db.update_task_description(self.task_id, value)

    def save_attachments(self, instance, value):
        if self.task_id:
            self.db.update_task_attachments(self.task_id, value)

    def complete_task(self, instance):
        if self.task_id:
            self.db.complete_task(self.task_id)
            main_screen = self.manager.get_screen('main')
            main_screen.refresh_task_list()
            self.manager.current = 'main'

    def go_back(self, instance):
        self.parent.current = 'main'