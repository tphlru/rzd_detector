# deploy.py
from pyinfra.operations import files, systemd, server

# TODO:
# создавать виртуальные окружения pyenv, учитывать в .service
# Устанавливать requirements.txt, при обновлении тоже


def deploy(pyenvpath):
	# Создаём каталоги, если их нет
	for dir in ['/opt/monitor', '/opt/piworker']:
		files.directory(
			name=f'Создание каталога {dir}',
			path=dir,
			_sudo=True
		)

	# Скрипты
	files.put(
		name='GitHub monitor script',
		src='files/github_monitor.py',
		dest='/opt/monitor/github_monitor.py'
	)

	files.put(
		name='PiWorker script',
		src='../piworker.py',
		dest='/opt/piworker/piworker.py'
	)

	# Сервисы systemd
	files.put(
		name='GitHub monitor service',
		src='files/github_monitor.service',
		dest='/etc/systemd/system/github_monitor.service'
	)

	files.put(
		src='files/piworker.service',
		dest='/etc/systemd/system/piworker.service'
	)

	# Перезагрузка и запуск
	server.shell('systemctl daemon-reload')

	for service in ['github_monitor', 'logs_monitor', 'piworker']:
		systemd.service(
			service,
			running=True,
			enabled=True
		)

if __name__ == '__main__':
	deploy('/home/timpy1/.pyenv/bin/pyenv')