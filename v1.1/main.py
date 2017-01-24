from aiohttp import web
import aiohttp_jinja2
import jinja2
import subprocess

print('test')
# функция пишет цифру 1, если галочка стоит
def write_status(enabled):
    f = open('log.txt', 'w', encoding='utf-8')
    if enabled:
        f.write('1')
    else:
        f.write('0')


# функция читает log.txt и возвращает True, если enabled
def read_status():
    f = open('log.txt', 'r', encoding='utf-8')
    return f.readline() == '1'


# функция для вкл\выкл\перезапуска демона
def demon_control(action):
    if action == "Stop":
        subprocess.check_output('sudo /etc/init.d/minidlna stop', shell=True)
    elif action == "Start":
        subprocess.check_output('sudo /etc/init.d/minidlna start', shell=True)
    elif action == "Restart":
        subprocess.check_output('sudo /etc/init.d/minidlna restart',
                                shell=True)


# функция определяет статус демона (работает или нет)
def get_status():
    return bool(
        subprocess.check_output('ps ax | grep minidlna | grep -v grep; exit 0',
                                shell=True))


# Пишем хэндлер
@aiohttp_jinja2.template('index.html')
async def handler(request):
    return {'form_enabled': read_status(), 'status': get_status()}


@aiohttp_jinja2.template('index.html')
async def action_handler(request):
    # Получаем данные
    data = await request.post()
    # Присутствие этой переменной говорит что галочка была отмечена
    form_enabled = data.get('form-toggle')
    write_status(form_enabled)
    # Получаем название кнопки
    action = data.get('action')
    # Пинаем демона функцией
    demon_control(action)
    return {'form_enabled': form_enabled, 'status': get_status(),
            'action': action}


# Запускаем наше приложение
app = web.Application()
app.router.add_route('GET', '/', handler)
app.router.add_route('POST', '/', action_handler)
aiohttp_jinja2.setup(app,
                     loader=jinja2.FileSystemLoader('./templates'))
web.run_app(app)
