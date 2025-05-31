import sqlite3


class Database:
    def __init__(self, db_name='todo.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
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

    def add_task(self, title, tags):
        self.cursor.execute(
            'INSERT INTO tasks (title, tags, description, attachments, completed) VALUES (?, ?, ?, ?, ?)',
            (title, tags, '', '', 0)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_active_tasks(self):
        self.cursor.execute('SELECT id, title, tags FROM tasks WHERE completed = 0')
        return self.cursor.fetchall()

    def get_task_details(self, task_id):
        self.cursor.execute('SELECT title, tags, description, attachments FROM tasks WHERE id = ?', (task_id,))
        return self.cursor.fetchone()

    def update_task_description(self, task_id, description):
        self.cursor.execute('UPDATE tasks SET description = ? WHERE id = ?', (description, task_id))
        self.conn.commit()

    def update_task_attachments(self, task_id, attachments):
        self.cursor.execute('UPDATE tasks SET attachments = ? WHERE id = ?', (attachments, task_id))
        self.conn.commit()

    def complete_task(self, task_id):
        self.cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()