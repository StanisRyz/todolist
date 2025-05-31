from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.app import App

class SelectableLabel(RecycleDataViewBehavior, FocusBehavior, Label):
    selected = BooleanProperty(False)
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