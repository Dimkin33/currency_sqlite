from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import json


class OurHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, currency):
        self.currency = currency
        super().__init__(request, client_address, server)

    def send_json_response(self, data, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=UTF-8')
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))

    def file_page(self, filename: str = 'index.html'):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()

        with open(filename, 'rb') as f:
            self.wfile.write(f.read())
    
    def get_currencies(self):
        currencies = self.currency.get_currencies()
        self.send_json_response(currencies)

    def do_POST(self):
        if self.path == '/currencies':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Парсим данные формы
                data = {}
                for pair in post_data.decode('utf-8').split('&'):
                    key, value = pair.split('=')
                    data[key] = value
                
                # Проверяем наличие всех необходимых полей
                required_fields = ['name', 'code', 'sign']
                for field in required_fields:
                    if field not in data:
                        error = json.dumps({'error': f'Отсутствует поле {field}'}, ensure_ascii=False)
                        self.send_json_response(error, HTTPStatus.BAD_REQUEST)
                        return
                    if not data[field].strip():
                        error = json.dumps({'error': f'Поле {field} не может быть пустым'}, ensure_ascii=False)
                        self.send_json_response(error, HTTPStatus.BAD_REQUEST)
                        return
                
                self.currency.add_currency(data['name'], data['code'], data['sign'])
                response_message = json.dumps({'message': 'Валюта успешно добавлена'}, ensure_ascii=False)
                self.send_json_response(response_message, HTTPStatus.CREATED)
            except ValueError as e:
                error = json.dumps({'error': str(e)}, ensure_ascii=False)
                self.send_json_response(error, HTTPStatus.BAD_REQUEST)
            except Exception as e:
                error = json.dumps({'error': str(e)}, ensure_ascii=False)
                self.send_json_response(error, HTTPStatus.INTERNAL_SERVER_ERROR)

        elif self.path == '/exchangeRates':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Парсим данные формы
                data = {}
                for pair in post_data.decode('utf-8').split('&'):
                    key, value = pair.split('=')
                    data[key] = value
                
                # Проверяем наличие всех необходимых полей
                required_fields = ['baseCurrencyCode', 'targetCurrencyCode', 'rate']
                for field in required_fields:
                    if field not in data:
                        error = json.dumps({'error': f'Отсутствует поле {field}'}, ensure_ascii=False)
                        self.send_json_response(error, HTTPStatus.BAD_REQUEST)
                        return
                    if not data[field].strip():
                        error = json.dumps({'error': f'Поле {field} не может быть пустым'}, ensure_ascii=False)
                        self.send_json_response(error, HTTPStatus.BAD_REQUEST)
                        return
                
                # Проверяем, что rate является числом
                try:
                    rate = float(data['rate'])
                    if rate <= 0:
                        error = json.dumps({'error': 'Курс обмена должен быть положительным числом'}, ensure_ascii=False)
                        self.send_json_response(error, HTTPStatus.BAD_REQUEST)
                        return
                except ValueError:
                    error = json.dumps({'error': 'Курс обмена должен быть числом'}, ensure_ascii=False)
                    self.send_json_response(error, HTTPStatus.BAD_REQUEST)
                    return
                
                self.currency.add_exchange_rate(
                    data['baseCurrencyCode'],
                    data['targetCurrencyCode'],
                    rate
                )
                response_message = json.dumps({'message': 'Курс обмена успешно добавлен'}, ensure_ascii=False)
                self.send_json_response(response_message, HTTPStatus.CREATED)
            except ValueError as e:
                if "уже существует" in str(e):
                    error = json.dumps({'error': str(e)}, ensure_ascii=False)
                    self.send_json_response(error, HTTPStatus.CONFLICT)
                elif "не найдена" in str(e):
                    error = json.dumps({'error': str(e)}, ensure_ascii=False)
                    self.send_json_response(error, HTTPStatus.NOT_FOUND)
                else:
                    error = json.dumps({'error': str(e)}, ensure_ascii=False)
                    self.send_json_response(error, HTTPStatus.BAD_REQUEST)
            except Exception as e:
                error = json.dumps({'error': str(e)}, ensure_ascii=False)
                self.send_json_response(error, HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, 'Page not found')

    def do_GET(self):
        if self.path == '/':
            print('index')
            self.file_page('index.html')
        elif self.path == '/currencies':
            self.get_currencies()
        elif self.path.startswith('/currency/'):
            code = self.path.split('/')[-1]
            currency = self.currency.get_currency_by_code(code)
            if currency:
                self.send_json_response(currency)
            else:
                error = json.dumps({'error': f'Валюта с кодом {code} не найдена'}, ensure_ascii=False)
                self.send_json_response(error, HTTPStatus.NOT_FOUND)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, 'Page not found')