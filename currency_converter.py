import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# --- НАСТРОЙКИ ---
HISTORY_FILE = 'history.json'
API_URL = 'https://api.exchangerate.host/convert'

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def load_history():
    """Загружает историю конвертаций из файла JSON."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_history(history):
    """Сохраняет историю конвертаций в файл JSON."""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except OSError as e:
        messagebox.showerror('Ошибка сохранения', f'Не удалось сохранить историю: {e}')

def get_currencies():
    """Запрашивает список доступных валют у API."""
    try:
        response = requests.get('https://api.exchangerate.host/symbols')
        data = response.json()
        # Возвращаем отсортированный список кодов валют
        return sorted(data['symbols'].keys())
    except requests.RequestException as e:
        messagebox.showerror('Ошибка сети', f'Не удалось получить список валют: {e}')
        return ['USD', 'EUR', 'RUB', 'GBP', 'JPY'] # Дефолтные значения

# --- ОСНОВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ ---

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Конвертер валют')
        self.root.geometry('700x500')
        self.root.resizable(False, False)

        # Загружаем данные
        self.history = load_history()
        self.currencies = get_currencies()

        # Создаем интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        """Создает все элементы графического интерфейса."""
        # --- Рамка для ввода данных ---
        input_frame = tk.LabelFrame(self.root, text='Конвертация', padx=10, pady=10)
        input_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky='ew')

        # Валюта "Из"
        tk.Label(input_frame, text='Из валюты:').grid(row=0, column=0, sticky='e')
        self.from_var = tk.StringVar(value='USD')
        self.from_menu = ttk.Combobox(input_frame, textvariable=self.from_var,
                                      values=self.currencies, state='readonly', width=10)
        self.from_menu.grid(row=0, column=1, padx=5, pady=5)

        # Валюта "В"
        tk.Label(input_frame, text='В валюту:').grid(row=1, column=0, sticky='e')
        self.to_var = tk.StringVar(value='EUR')
        self.to_menu = ttk.Combobox(input_frame, textvariable=self.to_var,
                                    values=self.currencies, state='readonly', width=10)
        self.to_menu.grid(row=1, column=1, padx=5, pady=5)

        # Сумма
        tk.Label(input_frame, text='Сумма:').grid(row=2, column=0, sticky='e')
        self.amount_entry = tk.Entry(input_frame)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        self.amount_entry.focus()  # Фокус на поле ввода при запуске

        # Кнопка конвертации
        tk.Button(input_frame, text='Конвертировать', bg='#4CAF50', fg='white',
                  command=self.convert).grid(row=3, column=0, columnspan=2,
                                             pady=15, ipadx=10)

        # Результат
        self.result_label = tk.Label(self.root, text='Результат: ', font=('Arial', 12))
        self.result_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # --- Таблица истории ---
        history_frame = tk.LabelFrame(self.root, text='История операций', padx=5, pady=5)
        history_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky='nsew')

        # Настройка весов для растягивания таблицы
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        cols = ('Дата', 'Операция', 'Результат')
        self.history_table = ttk.Treeview(history_frame, columns=cols,
                                          show='headings', selectmode='browse')

        for col in cols:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, anchor='center')

        # Полосы прокрутки
        yscroll = ttk.Scrollbar(history_frame, orient='vertical',
                                command=self.history_table.yview)
        xscroll = ttk.Scrollbar(history_frame, orient='horizontal',
                                command=self.history_table.xview)

        self.history_table.configure(yscroll=yscroll.set,
                                     xscroll=xscroll.set)

        # Размещение элементов в рамке истории
        self.history_table.grid(row=0, column=0, sticky='nsew')
        yscroll.grid(row=0, column=1, sticky='ns')
        xscroll.grid(row=1, column=0, sticky='ew')

    def convert(self):
        """Обрабатывает нажатие кнопки конвертации."""
        from_cur = self.from_var.get()
        to_cur = self.to_var.get()
        
        amount_str = self.amount_entry.get().strip()
        
        # Валидация ввода суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля.")
            if len(str(amount).split('.')[1]) > 2: # Проверка на более 2 знаков после запятой
                raise ValueError("Слишком много знаков после запятой.")
        except ValueError as e:
            messagebox.showwarning('Ошибка ввода', str(e))
            return

        try:
            params = {'from': from_cur.upper(), 'to': to_cur.upper(), 'amount': amount}
            response = requests.get(API_URL, params=params)
            data = response.json()
            
            if data.get('success'):
                result = data['result']
                date = data['date']
                
                # Добавляем в историю и сохраняем
                self.history.append({
                    'from': from_cur,
                    'to': to_cur,
                    'amount': amount,
                    'result': result,
                    'date': date
                })
                save_history(self.history)
                
                # Обновляем интерфейс
                self.update_history_table()
                self.result_label.config(
                    text=f'Результат: {result:.2f} {to_cur} (Курс на {date})'
                )
            else:
                error_info = data.get('error', {}).get('info', 'Неизвестная ошибка API.')
                messagebox.showerror('Ошибка API', error_info)
                
        except requests.RequestException as e:
            messagebox.showerror('Ошибка сети', f'Проверьте подключение к интернету.\n{e}')

    def update_history_table(self):
        """Обновляет данные в таблице истории."""
        for item in self.history_table.get_children():
            self.history_table.delete(item)
        
        for entry in reversed(self.history):  # Показываем свежие сверху
            op_text = f"{entry['amount']} {entry['from']} → {entry['to']}"
            res_text = f"{entry['result']:.2f} {entry['to']}"
            self.history_table.insert('', 'end', values=(entry['date'], op_text, res_text))


# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == '__main__':
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
