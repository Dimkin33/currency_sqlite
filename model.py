import sqlite3
import json

class Currency:
    def __init__(self):
        # Устанавливаем соединение с базой данных
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()

        # Создаем таблицу Currencies
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Currencies (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        sign TEXT
        )
        ''')

        # Сохраняем изменения и закрываем соединение
        connection.commit()
        connection.close()
    def add_currency(self, name, code, sign):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        
        # Проверяем, существует ли валюта с таким кодом
        cursor.execute('SELECT * FROM Currencies WHERE code = ?', (code,))
        if cursor.fetchone():
            connection.close()
            raise ValueError(f'Валюта с кодом {code} уже существует')
        
        # Если дубликата нет, добавляем новую валюту
        cursor.execute('INSERT INTO Currencies (name, code, sign) VALUES (?, ?, ?)', (name, code.upper(), sign))
        connection.commit()
        connection.close()
        
    def get_currencies(self):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT id, name, code, sign FROM Currencies')
        currencies = cursor.fetchall()
        connection.close()
        
        # Форматируем результат в список словарей
        result = []
        for id, name, code, sign in currencies:
            result.append({
                'id': id,
                'name': name,
                'code': code,
                'sign': sign
            })
        
        return json.dumps(result, ensure_ascii=False, indent=4)
    
    def get_currency_by_code(self, code):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        print(f'Поиск валюты с кодом: {code}')
        cursor.execute('SELECT id, name, code, sign FROM Currencies WHERE code = ?', (code.upper(),))
        currency = cursor.fetchone()
        connection.close()
        
        if not currency:
            return None
            
        id, name, code, sign = currency
        return json.dumps({
            'id': id,
            'name': name,
            'code': code,
            'sign': sign
        }, ensure_ascii=False, indent=4)

# Экспортируем класс Currency
__all__ = ['Currency']
        
