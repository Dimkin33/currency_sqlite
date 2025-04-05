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

        # Создаем таблицу ExchangeRates
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ExchangeRates (
        id INTEGER PRIMARY KEY,
        baseCurrencyCode TEXT NOT NULL,
        targetCurrencyCode TEXT NOT NULL,
        rate REAL NOT NULL,
        FOREIGN KEY (baseCurrencyCode) REFERENCES Currencies(code),
        FOREIGN KEY (targetCurrencyCode) REFERENCES Currencies(code),
        UNIQUE(baseCurrencyCode, targetCurrencyCode)
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

    def add_exchange_rate(self, base_currency_code, target_currency_code, rate):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        
        # Проверяем существование валют
        cursor.execute('SELECT code FROM Currencies WHERE code = ?', (base_currency_code.upper(),))
        if not cursor.fetchone():
            connection.close()
            raise ValueError(f'Базовая валюта с кодом {base_currency_code} не найдена')
            
        cursor.execute('SELECT code FROM Currencies WHERE code = ?', (target_currency_code.upper(),))
        if not cursor.fetchone():
            connection.close()
            raise ValueError(f'Целевая валюта с кодом {target_currency_code} не найдена')
        
        # Проверяем, существует ли курс
        cursor.execute('SELECT * FROM ExchangeRates WHERE baseCurrencyCode = ? AND targetCurrencyCode = ?',
                      (base_currency_code.upper(), target_currency_code.upper()))
        if cursor.fetchone():
            connection.close()
            raise ValueError(f'Курс обмена {base_currency_code}/{target_currency_code} уже существует')
        
        # Добавляем новый курс
        cursor.execute('''
            INSERT INTO ExchangeRates (baseCurrencyCode, targetCurrencyCode, rate)
            VALUES (?, ?, ?)
        ''', (base_currency_code.upper(), target_currency_code.upper(), rate))
        
        connection.commit()
        connection.close()

    def get_exchange_rates(self):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute('''
            SELECT baseCurrencyCode, targetCurrencyCode, rate 
            FROM ExchangeRates
        ''')
        rates = cursor.fetchall()
        connection.close()
        
        result = []
        for base_code, target_code, rate in rates:
            result.append({
                'baseCurrencyCode': base_code,
                'targetCurrencyCode': target_code,
                'rate': rate
            })
        
        return json.dumps(result, ensure_ascii=False, indent=4)

    def update_exchange_rate(self, base_currency_code, target_currency_code, rate):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        
        # Проверяем существование валютной пары
        cursor.execute('''
            SELECT er.id, 
                   bc.id as base_id, bc.name as base_name, bc.code as base_code, bc.sign as base_sign,
                   tc.id as target_id, tc.name as target_name, tc.code as target_code, tc.sign as target_sign,
                   er.rate
            FROM ExchangeRates er
            JOIN Currencies bc ON er.baseCurrencyCode = bc.code
            JOIN Currencies tc ON er.targetCurrencyCode = tc.code
            WHERE er.baseCurrencyCode = ? AND er.targetCurrencyCode = ?
        ''', (base_currency_code.upper(), target_currency_code.upper()))
        
        result = cursor.fetchone()
        if not result:
            connection.close()
            raise ValueError(f'Валютная пара {base_currency_code}/{target_currency_code} не найдена')
        
        # Обновляем курс
        cursor.execute('''
            UPDATE ExchangeRates 
            SET rate = ?
            WHERE baseCurrencyCode = ? AND targetCurrencyCode = ?
        ''', (rate, base_currency_code.upper(), target_currency_code.upper()))
        
        connection.commit()
        connection.close()
        
        # Формируем ответ
        return json.dumps({
            'id': result[0],
            'baseCurrency': {
                'id': result[1],
                'name': result[2],
                'code': result[3],
                'sign': result[4]
            },
            'targetCurrency': {
                'id': result[5],
                'name': result[6],
                'code': result[7],
                'sign': result[8]
            },
            'rate': rate
        }, ensure_ascii=False, indent=4)

    def get_exchange_rate_pairs(self):
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute('''
            SELECT er.baseCurrencyCode, er.targetCurrencyCode, 
                   bc.name as base_name, tc.name as target_name
            FROM ExchangeRates er
            JOIN Currencies bc ON er.baseCurrencyCode = bc.code
            JOIN Currencies tc ON er.targetCurrencyCode = tc.code
        ''')
        pairs = cursor.fetchall()
        connection.close()
        
        result = []
        for base_code, target_code, base_name, target_name in pairs:
            result.append({
                'baseCurrencyCode': base_code,
                'targetCurrencyCode': target_code,
                'baseName': base_name,
                'targetName': target_name
            })
        
        return json.dumps(result, ensure_ascii=False, indent=4)

        
