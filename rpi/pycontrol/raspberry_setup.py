# raspberry_setup.py
"""
Скрипт начальной настройки Raspberry Pi.
Запуск: pyinfra --user username --password "pass" inventory.py raspberry_setup.py
"""

from pyinfra.operations import apt, server, files
from pyinfra.facts.files import FindFiles
from pyinfra import host

username = 'timpy1'
pyenv = f"/home/{username}/.pyenv/bin/pyenv"


# Обновление системы
apt.update(
    name='Обновление apt кэша',
    _sudo=True
)
apt.upgrade(
    name='Установка обновлений',
    _sudo=True
)

# Установка Git
apt.packages(
    name='Установка git',
    packages=['git'],
    _sudo=True
)

# Установка системных зависимостей
apt.packages(
    name='Установка системных компонентов',
    packages=[
        'libssl-dev', 'zlib1g-dev', 'libbz2-dev', 'libreadline-dev',
        'libsqlite3-dev', 'llvm', 'libncurses5-dev', 'libncursesw5-dev',
        'xz-utils', 'tk-dev', 'libgdbm-dev', 'lzma', 'lzma-dev', 'tcl-dev',
        'libxml2-dev', 'libxmlsec1-dev', 'libffi-dev', 'liblzma-dev',
        'wget', 'curl', 'make', 'build-essential', 'openssl'
    ],
    _sudo=True
)

# Создание .bashrc если не существует
server.shell(
    name='Создание .bashrc',
    commands=[f'touch /home/{username}/.bashrc'],
)

check_if_installed = host.get_fact(FindFiles, "~/.pyenv/bin/pyenv", quote_path=True)

if "pyenv" not in check_if_installed:
    # Проверка и удаление старой установки pyenv
    server.shell(
        name='Удаление ~/.pyenv при наличии',
        commands=[f'rm -rf /home/{username}/.pyenv']
    )

    # Установка pyenv 
    server.shell(
        name='Установка pyenv',
        commands=[
            'curl https://pyenv.run | bash'
        ]
    )

    # Конфигурация .bashrc
    lines = [
        f'export PYENV_ROOT="/home/{username}/.pyenv"',
        'export PATH="$PYENV_ROOT/bin:$PATH"',
        'eval "$(pyenv init --path)"'
    ]
    lines = '\n'.join(lines)
    files.line(
        name='Добавление pyenv в .bashrc',
        path=f'/home/{username}/.bashrc',
        line=lines
    )

    # Python установка
    server.shell(
        commands=[
            f'. /home/{username}/.bashrc',
        ]
    )

    server.shell(
        name='Обновление pyenv и установка Python 3.10',
        commands=[
            f'{pyenv} update',
            f'{pyenv} install 3.10'
        ]
    )
else:
    print("pyenv уже установлен")



