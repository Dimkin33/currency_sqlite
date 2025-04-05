from http.server import HTTPServer
from server import OurHandler
from model import Currency

def run_server():
    # Создаем экземпляр Currency один раз при запуске
    currency = Currency()
    
    # Создаем функцию-фабрику для OurHandler
    def handler_factory(*args, **kwargs):
        return OurHandler(*args, **kwargs, currency=currency)
    
    # Создаем и запускаем сервер
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler_factory)
    print('Сервер запущен на порту 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
