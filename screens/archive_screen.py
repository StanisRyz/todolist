from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from widgets.selectable_label import SelectableLabel


class ArchiveScreen(Screen):

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = BoxLayout(orientation = 'vertical', spacing = 10, padding = 10)

        title_label = Label(
            text = 'Архив завершенных задач',
            size_hint = (1, None),
            height = 50,
            color = (1, 1, 1, 1),
            font_size = '20sp',
            bold = True,
        )
        layout.add_widget(title_label)

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
        self.refresh_task_list()
        layout.add_widget(self.task_list)

        back_button = Button(
            text = 'Назад',
            size_hint = (1, None),
            height = 50,
            background_color = (0.5, 0.3, 0.3, 1),
        )
        back_button.bind(on_press = self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def refresh_task_list(self):
        self.task_list.data = self.load_tasks()

    def load_tasks(self):
        tasks = []
        for row in self.db.get_completed_tasks():
            task_id, title, tags, completed_date = row
            display_text = f"[b]{title}[/b]"

            if completed_date:
                display_text += f"\n [size=10][color=888888]Завершено: {completed_date}[/color][/size]"

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

    def go_back(self, instance):
        self.manager.current = 'main'