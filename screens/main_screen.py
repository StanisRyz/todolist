from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from widgets.selectable_label import SelectableLabel


class MainScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Поле ввода задачи
        self.task_input = TextInput(
            hint_text='Введите задачу',
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
        )
        layout.add_widget(self.task_input)

        # Поле ввода тегов
        self.tags_input = TextInput(
            hint_text='Введите теги (через запятую)',
            multiline=False,
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
        )
        layout.add_widget(self.tags_input)

        # Кнопка добавления задачи
        add_button = Button(
            text='Добавить задачу',
            size_hint=(1, None),
            height=50,
            background_color=(0.3, 0.5, 0.7, 1),
        )
        add_button.bind(on_press=self.add_task)
        layout.add_widget(add_button)

        archive_button = Button(
            text = 'Показать архив',
            size_hint = (1, None),
            height = 50,
            background_color = (0.4, 0.4, 0.6, 1),
        )
        archive_button.bind(on_press = self.show_archive)
        layout.add_widget(archive_button)

        # Список задач
        self.task_list = RecycleView(
            size_hint=(1, 1),
            bar_width=10,
            bar_color=(0.5, 0.5, 0.5, 1),
        )

        # Менеджер компоновки для списка задач
        layout_manager = RecycleBoxLayout(
            default_size=(None, 50),
            default_size_hint=(1, None),
            orientation='vertical',
            size_hint_y=None,
            spacing=5,
        )
        layout_manager.bind(minimum_height=layout_manager.setter('height'))
        self.task_list.layout_manager = layout_manager
        self.task_list.add_widget(layout_manager)
        self.task_list.viewclass = SelectableLabel

        # Загрузка активных задач (completed = 0)
        self.refresh_task_list()

        layout.add_widget(self.task_list)
        self.add_widget(layout)

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        tags = self.tags_input.text.strip()

        if task_text:
            # Добавляем задачу в базу данных
            self.db.add_task(task_text, tags)

            # Очищаем поля ввода
            self.task_input.text = ''
            self.tags_input.text = ''

            # Обновляем список задач
            self.refresh_task_list()

    def refresh_task_list(self):
        self.task_list.data = self.load_tasks()

    def load_tasks(self):
        """Загружает только активные задачи (completed = 0)"""
        tasks = []

        # Получаем только активные задачи из базы данных
        for task_id, title, tags in self.db.get_active_tasks():
            display_text = f"[b]{title}[/b]"

            # Форматируем теги, если они есть
            if tags:
                cleaned_tags = ', '.join(
                    tag.strip() for tag in tags.split(',')
                    if tag.strip()
                )
                if cleaned_tags:
                    display_text += f"\n[size=12][color=aaaaaa]Теги: {cleaned_tags}[/color][/size]"

            tasks.append({
                'text': display_text,
                'selected': False,
                'task_id': task_id
            })

        return tasks

    def reset_selection(self):
        """Сбрасывает выделение всех задач"""
        for item in self.task_list.data:
            item['selected'] = False
        self.task_list.refresh_from_data()

    def show_archive(self, instance):
        archive_screen = self.manager.get_screen('archive')
        archive_screen.refresh_task_list()
        self.manager.current = 'archive'