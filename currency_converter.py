import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

HISTORY_FILE = 'history.json'
API_URL = 'https://api.exchangerate.host/convert'

# Загрузка истории
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

# Сохранение истории
def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

# Получение списка валют
def get_currencies():
    try:
        resp = requests.get('https://api.exchangerate.host/symbols')
        data = resp.json()
        return sorted(data['symbols'].keys())
    except Exception as e:
        messagebox.showerror('Ошибка', f'Не удалось получить список валют: {e}')
        return ['USD', 'EUR', 'RUB']

# Конвертация валюты
def convert():
    from_cur = from_var.get()
    to_cur = to_var.get()
    amount_str = amount_entry.get()

    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror('Ошибка', 'Сумма должна быть положительным числом')
        return

    try:
        params = {'from': from_cur, 'to': to_cur, 'amount': amount}
        resp = requests.get(API_URL, params=params)
        data = resp.json()
        if data.get('success'):
            result = data['result']
            history.append({
                'from': from_cur,
                'to': to_cur,
                'amount': amount,
                'result': result,
                'date': data['date']
            })
            save_history(history)
            update_history_table()
            result_label.config(text=f'Результат: {result:.2f} {to_cur}')
        else:
            messagebox.showerror('Ошибка', f'Ошибка API: {data.get("error", "неизвестная ошибка")}')
    except Exception as e:
        messagebox.showerror('Ошибка', f'Не удалось выполнить запрос:Вот подробная пошаговая инструкция по созданию GUI-приложения «Currency Converter» (Конвертер валют) на Python с использованием Tkinter, внешнего API, сохранения истории и Git.
