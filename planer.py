import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime
import json
import os

FILE_NAME = 'tasks.json' # сохранение задач
DATE_FORMAT = '%d-%m-%Y'  # день-месяц-год

class PlannerApp: # класс планера
    def __init__(self, root): # Создаем конструктор
        # Главное окно
        self.root = root
        self.root.title('Планер задач')
        self.root.geometry('800x650')

        # Задачи и фильтрация
        self.tasks = []
        self.current_date_filter = None
        self.current_status_filter = None  # None / True / False

        # Поле ввода
        tk.Label(root, text='Введите текст задачи').pack(pady=(10, 0))
        self.entry = tk.Entry(root, width=80)
        self.entry.pack(pady=5)

        # Календарь основной с форматом dd-mm-yyyy
        self.calendar = Calendar(root, selectmode='day', date_pattern='dd-mm-yyyy')
        self.calendar.pack(pady=5)

        # Контейнер для размещения кнопок
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        # Создание кнопок
        tk.Button(btn_frame, text='Добавить', width=15, command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text='Редактировать', width=15, command=self.edit_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text='Выполнено / Не выполнено', width=22, command=self.toggle_done).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text='Удалить', width=15, command=self.delete_task).grid(row=0, column=3, padx=5)

        tk.Button(btn_frame, text='Показать на текущую дату', width=25, command=self.filter_by_date).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text='Показать все', width=20, command=self.show_all).grid(row=1, column=2, columnspan=2, pady=5)
        tk.Button(btn_frame, text='Выполненные', width=20, command=self.show_done).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text='Невыполненные', width=20, command=self.show_not_done).grid(row=2, column=2, columnspan=2, pady=5)

        # Виджет для отображения списка задач
        self.tasks_listbox = tk.Listbox(root, width=110, height=20)
        self.tasks_listbox.pack(pady=10)

        self.load_tasks() # загрузка задач при старте
        self.refresh_listbox() # обновить список и отобразить текущие задачи

    # Основная логика

    def add_task(self): # добавить задачу
        text = self.entry.get().strip()
        date = self.calendar.get_date()
        if not text:
            messagebox.showwarning('Ошибка', 'Введите задачу!')
            return
        self.tasks.append({'text': text, 'date': date, 'done': False})
        self.entry.delete(0, tk.END) # очиститть поле после ввода задачи
        self.save_tasks()
        self.refresh_listbox()

    def edit_task(self): # редактировать задачу
        selected = self.tasks_listbox.curselection()
        if not selected:
            messagebox.showwarning('Ошибка', 'Выберите задачу!')
            return
        task_text = self.tasks_listbox.get(selected[0])
        for i, task in enumerate(self.tasks):
            display_text = f'[✔]' if task['done'] else '[ ]'
            display_text += f" {task['date']} — {task['text']}"
            if display_text == task_text:
                self.edit_task_window(i)
                break

    def edit_task_window(self, index): # окно редактирования задачи
        task = self.tasks[index]
        edit_win = tk.Toplevel(self.root)
        edit_win.title('Редактировать задачу')
        edit_win.geometry('500x500')

        tk.Label(edit_win, text='Текст задачи:').pack(anchor='w', padx=10, pady=(10, 0))
        entry = tk.Entry(edit_win, width=60)
        entry.pack(fill='x', padx=10, pady=5)
        entry.insert(0, task['text'])

        tk.Label(edit_win, text='Дата задачи:').pack(anchor='w', padx=10, pady=(10, 0))
        cal = Calendar(edit_win, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(padx=10, pady=5)

        # Устанавливаем дату
        day, month, year = map(int, task['date'].split('-'))
        cal.selection_set(datetime(year, month, day).date())

        tk.Button(edit_win, text='Сохранить', width=20,
                  command=lambda: self.save_edited_task(index, entry.get(), cal.get_date(), edit_win)).pack(pady=10)

    def save_edited_task(self, index, new_text, new_date, window): # сохранение отредактированной задачи
        if not new_text.strip():
            messagebox.showwarning('Ошибка', 'Введите текст задачи')
            return
        self.tasks[index]['text'] = new_text.strip()
        self.tasks[index]['date'] = new_date
        self.save_tasks()
        self.refresh_listbox()
        window.destroy()

    # Статус "Выполнено" или "Не выполнено" и удаление задачи

    def toggle_done(self): # выполенено, поставить галочку
        selected = self.tasks_listbox.curselection()
        if not selected:
            messagebox.showwarning('Ошибка', 'Выберите задачу!')
            return
        task_text = self.tasks_listbox.get(selected[0])
        for i, task in enumerate(self.tasks):
            display_text = f'[✔]' if task['done'] else '[ ]'
            display_text += f" {task['date']} — {task['text']}"
            if display_text == task_text:
                task['done'] = not task['done']
                break
        self.save_tasks()
        self.refresh_listbox()

    def delete_task(self): # удаление задачи
        selected = self.tasks_listbox.curselection()
        if not selected:
            messagebox.showwarning('Ошибка', 'Выберите задачу')
            return
        task_text = self.tasks_listbox.get(selected[0])
        for i, task in enumerate(self.tasks):
            display_text = f'[✔]' if task['done'] else '[ ]'
            display_text += f" {task['date']} — {task['text']}"
            if display_text == task_text:
                del self.tasks[i]
                break
        self.save_tasks()
        self.refresh_listbox()

    # Фильтры. По дате, выпонено/не выполнено, показать все задачи

    def filter_by_date(self): # показать на текущую дату
        self.current_date_filter = self.calendar.get_date()
        self.current_status_filter = None
        self.refresh_listbox()

    def show_done(self): # выполнено
        self.current_status_filter = True
        self.refresh_listbox()
 
    def show_not_done(self): # не выполнено
        self.current_status_filter = False
        self.refresh_listbox()

    def show_all(self): # показать все
        self.current_date_filter = None
        self.current_status_filter = None
        self.refresh_listbox()

    # Обновление списка 

    def refresh_listbox(self):
        self.tasks_listbox.delete(0, tk.END)
       # Фильтруем задачи по дате и статусу, если фильтры заданы
        filtered_tasks = [
            task for task in self.tasks
            if (self.current_date_filter is None or task['date'] == self.current_date_filter) and
               (self.current_status_filter is None or task['done'] == self.current_status_filter)
        ]
        # Превращает 'dd-mm-yyyy' в объект datetime, для правильной сортировки по дате
        def date_key(task):
            return datetime.strptime(task['date'], DATE_FORMAT)
        filtered_tasks.sort(key=date_key) # Сортируем задачи по возрастанию даты

        for task in filtered_tasks:
            status = '[✔]' if task['done'] else '[ ]'
            display_text = f"{status} {task['date']} — {task['text']}"
            self.tasks_listbox.insert(tk.END, display_text)
            if task['done']:
                self.tasks_listbox.itemconfig(tk.END, fg='gray')

    # Работа с файлом 
    def save_tasks(self):
        with open(FILE_NAME, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                try:
                    self.tasks = json.load(f)
                    for task in self.tasks: # конвертируем старые даты ISO в dd-mm-yyyy
                        parts = task['date'].split('-')
                        if len(parts[0]) == 4:  # yyyy-mm-dd
                            task['date'] = f'{parts[2]}-{parts[1]}-{parts[0]}'
                except json.JSONDecodeError:
                    self.tasks = []
        else:
            self.tasks = []

    # Запуск
if __name__ == '__main__':
    root = tk.Tk()
    app = PlannerApp(root)
    root.mainloop()
