import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")

        # API ключ (замените на свой)
        self.api_key = "YOUR_API_KEY"
        self.history_file = "conversion_history.json"
        self.history = []

        self.load_history()
        self.create_widgets()
        self.update_currencies()

    def create_widgets(self):
        # Фрейм выбора валют
        currency_frame = ttk.Frame(self.root)
        currency_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(currency_frame, text="Из:").grid(row=0, column=0, sticky="w")
        self.from_currency = ttk.Combobox(currency_frame, width=10)
        self.from_currency.grid(row=0, column=1, padx=5)

        ttk.Label(currency_frame, text="В:").grid(row=0, column=2, sticky="w")
        self.to_currency = ttk.Combobox(currency_frame, width=10)
        self.to_currency.grid(row=0, column=3, padx=5)

        # Поле ввода суммы
        amount_frame = ttk.Frame(self.root)
        amount_frame.pack(pady=5, padx=20, fill="x")

        ttk.Label(amount_frame, text="Сумма:").pack(side="left")
        self.amount_entry = ttk.Entry(amount_frame, width=20)
        self.amount_entry.pack(side="left", padx=5)

        # Кнопка конвертации
        ttk.Button(self.root, text="Конвертировать",
                   command=self.convert_currency).pack(pady=10)

        # Результат
        self.result_label = ttk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.pack(pady=5)

        # Таблица истории
        history_frame = ttk.Frame(self.root)
        history_frame.pack(pady=10, padx=20, fill="both", expand=True)

        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_history()

    def update_currencies(self):
        """Получение списка валют"""
        try:
            response = requests.get(f"https://api.exchangerate-api.com/v4/latest/USD")
            data = response.json()
            currencies = list(data['rates'].keys())
            self.from_currency['values'] = currencies
            self.to_currency['values'] = currencies
            # Устанавливаем значения по умолчанию
            self.from_currency.set('USD')
            self.to_currency.set('EUR')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить валюты: {e}")

    def convert_currency(self):
        """Конвертация валюты"""
        # Проверка ввода
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительным числом")
        except ValueError as e:
            messagebox.showwarning("Ошибка ввода", str(e))
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if not from_curr or not to_curr:
            messagebox.showwarning("Ошибка", "Выберите валюты")
            return

        try:
            # Получаем курс через API
            response = requests.get(
                f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            )
            data = response.json()

            if to_curr in data['rates']:
                rate = data['rates'][to_curr]
                result = amount * rate

                # Отображаем результат
                self.result_label.config(
                    text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"
                )

                # Добавляем в историю
                conversion = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": amount,
                    "from": from_curr,
                    "to": to_curr,
                    "result": result
                }
                self.history.append(conversion)
                self.save_history()
                self.refresh_history()
            else:
                messagebox.showerror("Ошибка", "Неизвестный код валюты")
        except Exception as e:
            messagebox.showerror("Ошибка API", f"Ошибка при конвертации: {e}")

    def load_history(self):
        """Загрузка истории из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []
        else:
            self.history = []

    def save_history(self):
        """Сохранение истории в файл"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def refresh_history(self):
        """Обновление таблицы истории"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for record in self.history[-10:]:  # Последние 10 записей
            self.tree.insert("", "end", values=(
                record["date"],
                f"{record['amount']:.2f}",
                record["from"],
                record["to"],
                f"{record['result']:.2f}"
            ))