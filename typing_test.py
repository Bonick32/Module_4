import tkinter as tk
from tkinter import messagebox
import tkinter.simpledialog
# import names
import time
import difflib
import pandas as pd
from datetime import datetime
import random
import requests
import re
from bs4 import BeautifulSoup
import os

start_time = time.time()

# Проверяем наличие хотя бы одного символа латиницы
def contains_latin(text):
    return bool(re.search(r'[a-zA-Z]', text))

# Функция для извлечения текста с веб-страницы
def fetch_text_from_url():
    url = tkinter.simpledialog.askstring("Сайт", "Скопируйте ссылку с сайта для вставки текста. \n "
                                                 "используйте комбинацию Ctrl+V на английской раскладке. \n" 
                                                 "Нажмите отмена, чтобы воспользоваться сайтом по умолчанию")
    if url is None:
        url = 'https://cyberleninka.ru/article/n/l-n-tolstoy-i-angliyskaya-literatura-predystoriya-tvorcheskogo-dialoga'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлекаем текст из всех параграфов
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    return text

# Извлекаем из текста со страницы 80 слов
def get_random_segment_cyril(segment_length=80):

    text = fetch_text_from_url()
    words = text.split()
    if len(words) < segment_length:
        return text  # Если текста меньше, чем длина отрезка, возвращаем весь текст

    # Ищем подходящие отрезки
    valid_segments = []
    for i in range(len(words) - segment_length + 1):
        segment = ' '.join(words[i:i + segment_length])
        if not contains_latin(segment):
            valid_segments.append(segment)

    if not valid_segments:
        return None  # Если не найдено подходящих отрезков, возвращаем None

    # Выбираем случайный отрезок из найденных
    return random.choice(valid_segments)



# def gen_text(n=5):
#     return ', '.join([names.get_full_name() for _ in range(n)])

# def start_typing():
#     global start_time
#     text_to_type = get_random_segment_cyril()
#     text_display.delete(1.0, tk.END)
#     text_display.insert(tk.END, text_to_type)
#
#     messagebox.showinfo("Приготовьтесь", "Приготовьтесь вводить текст. Через 3 секунды автоматически "
#                                          "появится курсор.")
#     root.after(3000, begin_typing)  # Запускаем таймер на 3 секунды


def start_typing():
    global start_time
    text_to_type = get_random_segment_cyril()

    if not text_to_type:  # Проверяем, пустое ли поле
        messagebox.showwarning("Внимание", "Поле для ввода пустое. Пожалуйста, введите хотя бы одно слово.")

    text_display.delete(1.0, tk.END)
    text_display.insert(tk.END, text_to_type)

    # Создаем новое окно для сообщения
    message_window = tk.Toplevel()
    message_window.title("Приготовьтесь")

    # Создаем метку с сообщением
    label = tk.Label(message_window, text="Приготовьтесь вводить текст. Через 3 секунды автоматически "
                                          "появится курсор.", padx=20, pady=20)
    label.pack()

    # Закрываем окно через 3 секунды и запускаем begin_typing
    message_window.after(3000, lambda: [message_window.destroy(), begin_typing()])

def begin_typing():
    global start_time
    start_time = time.time()
    user_input_text.focus()  # Устанавливаем фокус на поле ввода

def submit_input():
    global start_time
    stop_time = time.time()
    user_time = stop_time - start_time

    user_text = user_input_text.get("1.0", tk.END).strip()
    text_to_type = text_display.get("1.0", tk.END).strip()
    sim = similarity(user_text, text_to_type)

    output(user_text, sim, user_time)

def similarity(s1, s2):
    matcher = difflib.SequenceMatcher(None, s1, s2)
    return matcher.ratio()

def output(user_text, sim, user_time):
    messagebox.showinfo("Результаты", f'Вы напечатали {len(user_text)} '
                                      f'символов за {round(user_time, 2)} секунд.\n'
                                      f'Ваша точность составила {int(sim * 100)} % '
                                      f'и итог: {int(len(user_text) / user_time * 60 * sim)} символов в минуту')

    name = tkinter.simpledialog.askstring("Имя", "Введите ваше имя:")
    if name:
        # Проверяем, существует ли файл table.csv
        if not os.path.exists('table.csv'):
            # Если файл не существует, создаем его с заголовками
            df = pd.DataFrame(columns=["Name", "Number of characters", "Time (sec)", "Accuracy (%)", "Date"])
            df.to_csv('table.csv', index=False)
        if not os.path.exists('table.xlsx'):
            # Если файл не существует, создаем его с заголовками
            df = pd.DataFrame(columns=["Name", "Number of characters", "Time (sec)", "Accuracy (%)", "Date"])
            df.to_excel('table.xlsx', index=False)

        try:
            # Читаем существующий файл
            df = pd.read_csv('table.csv')
            # Добавляем новую строку с данными
            df.loc[len(df)] = [name, len(user_text), round(user_time, 2), int(sim * 100), datetime.today()]
            # Сохраняем обновленный DataFrame в файл
            df.to_csv('table.csv', index=False)
            df.to_excel("table.xlsx", index=False, engine='openpyxl')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")


def disable_selection(event):
    # Запрещаем выделение текста
    return "break"

# Создаем основное окно
root = tk.Tk()
root.title("Тест на скорость печати")
root.geometry("730x290")

# Поле для отображения текста
text_display = tk.Text(root, wrap=tk.WORD, height=7, width=90)
text_display.pack()

# Привязываем события мыши и клавиатуры к функции disable_selection
text_display.bind("<Button-1>", disable_selection)  # Левый клик мыши
text_display.bind("<Control-Button-1>", disable_selection)  # Левый клик с Ctrl
text_display.bind("<Shift-Button-1>", disable_selection)  # Левый клик с Shift
text_display.bind("<KeyPress>", disable_selection)  # Нажатие клавиш

# Поле для ввода текста пользователем
user_input_text = tk.Text(root, wrap=tk.WORD, height=7, width=90)
user_input_text.pack()

# Кнопка для начала теста
start_button = tk.Button(root, text="Начать", command=start_typing)
start_button.pack()

# Кнопка для отправки введенного текста
submit_button = tk.Button(root, text="Отправить", command=submit_input)
submit_button.pack()

root.mainloop()
