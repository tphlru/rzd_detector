# raspberry_setup.py
"""
Скрипт начальной настройки Raspberry Pi.
Запуск: pyinfra --user username --password "pass" inventory.py raspberry_setup.py
"""

from pyinfra.operations import apt, systemd, files, pip
from pyinfra.facts.server import User
from pyinfra import host
from pyinfra.api import FactBase
import toml


class Uuid(FactBase):
    def command(self):
        return """
        python3 -c 'import uuid; print("".join(["{:02x}".format((uuid.getnode() >> i) & 0xff) 
        for i in range(0, 48, 8)][::-1]))'"""

    def process(self, output):
        return "\n".join(output)


username = host.get_fact(User)
print(f"Имя пользователя: {username}")
pyenv = f"/home/{username}/.pyenv/bin/pyenv"

device_id = host.get_fact(Uuid)
print(f"Уникальный идентификатор устройства: {device_id}")

with open("devices.toml", "r") as f:
    devices = toml.load(f)
    print(devices)

devices = devices or {}
devices[device_id] = username

with open("devices.toml", "w") as f:
    toml.dump(devices, f)

# Обновление системы
# apt.update(
#     name='Обновление apt кэша',
#     _sudo=True
# )
# apt.upgrade(
#     name='Установка обновлений',
#     _sudo=True
# )

# Установка Git
apt.packages(name="Установка git", packages=["git"], _sudo=True)

# Установка системных зависимостей
apt.packages(
    name="Установка системных компонентов",
    packages=[
        "python3-full",  # Python
        "python3-pip",  # pip
        "build-essential",  # компиляция
        "libssl-dev",  # безопасность
        "zlib1g-dev",  # сжатие
        "libffi-dev",  # расширения Python
        "make",  # сборка
        "libreadline-dev",  # интерактивная оболочка
        "libsqlite3-dev",  # поддержка SQLite
        "wget",  # загрузка пакетов
        "curl",  # загрузка пакетов
        "python3-picamera2",  # новая версия API камеры
        "libcamera-dev",  # libcamera
        "libcamera-tools",  # утилиты libcamera
        "libatlas-base-dev",  # утилиты libcamera
        "ffmpeg",  # ffmpeg
        "ufw",  # фаервол
    ],
    _sudo=True,
)

# Создадим рабочую директорию
files.directory(
    name="Создание рабочей директории",
    path=f"/home/{username}/rpi/",
    present=True,
    force=False,
    force_backup=False,
)

files.put(
    name="Создание файла скрипта rpi-updater",
    src="files/requirements.txt",
    dest=f"/home/{username}/rpi/requirements.txt",
    _sudo=True,
)

pip.packages(
    name="Установка зависимостей (python)",
    present=True,
    requirements=f"/home/{username}/rpi/requirements.txt",
    pip="pip",
    extra_install_args="--break-system-packages",
)

# Положить файлы скриптов и сервисов. В сервисах шаблон.

files.template(
    name="Создание файла сервиса rpi-updater",
    src="files/templates/rpi-updater.service.j2",
    dest="/etc/systemd/system/rpi-updater.service",
    homeusername=username,
    _sudo=True,
)

files.template(
    name="Создание файла сервиса PiWorker",
    src="files/templates/piworker.service.j2",
    dest="/etc/systemd/system/piworker.service",
    homeusername=username,
    _sudo=True,
)

files.put(
    name="Создание файла скрипта rpi-updater",
    src="files/rpi-updater.py",
    dest=f"/home/{username}/rpi/rpi-updater.py",
    _sudo=True,
)

files.put(
    name="Создание файла скрипта PiWorker",
    src="files/piworker.py",
    dest=f"/home/{username}/rpi/piworker.py",
    _sudo=True,
)

files.put(
    name="Добавление модуля pre_start",
    src="files/pre_start.py",
    dest=f"/home/{username}/rpi/pre_start.py",
    _sudo=True,
)

sudoers_content = f"""
%{username} ALL= NOPASSWD: /bin/systemctl daemon-reload
%{username} ALL= NOPASSWD: /bin/systemctl stop piworker
%{username} ALL= NOPASSWD: /bin/systemctl start piworker
%{username} ALL= NOPASSWD: /bin/systemctl restart piworker
%{username} ALL= NOPASSWD: /bin/systemctl stop rpi-updater
%{username} ALL= NOPASSWD: /bin/systemctl start rpi-updater
%{username} ALL= NOPASSWD: /bin/systemctl restart rpi-updater
"""

# Создаем файл с правильными правами доступа
files.file(
    name="Создание sudoers файла",
    path="/etc/sudoers.d/service-control",
    present=True,
    mode=440,  # r--r----- права доступа требуемые для sudoers файлов
    user="root",
    group="root",
    touch=True,
    _sudo=True,
)

files.block(
    name="Добавление sudoers правил",
    path="/etc/sudoers.d/service-control",
    present=True,
    before=False,
    after=False,
    content=sudoers_content,
    _sudo=True,
)


systemd.daemon_reload(user_mode=False, machine=None, user_name=None, _sudo=True)

# Создание сервисов
systemd.service(
    "rpi-updater",
    name="Создание сервиса rpi-updater",
    running=True,
    enabled=True,
    daemon_reload=False,
    _sudo=True,
)

systemd.service(
    "piworker",
    name="Создание сервиса PiWorker",
    running=True,
    enabled=True,
    daemon_reload=False,
    _sudo=True,
)

systemd.service(
    "rpi-updater",
    name="Перезапуск rpi-updater после обновления",
    running=True,
    restarted=True,
    enabled=True,
    _sudo=True,
)

systemd.service(
    "piworker",
    name="Перезапуск PiWorker после обновления",
    running=True,
    restarted=True,
    enabled=True,
    _sudo=True,
)
