import time
import subprocess
import sys
import git
from pathlib import Path
import logging
import os
import pwd

from piworker import get_current_device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPO_PATH = 'https://github.com/tphlru/rzd_detector.git'
username = get_current_device() or pwd.getpwuid(os.getuid()).pw_name


class GitUpdater:
	def __init__(self, repo_url, local_path, branch, update_interval=300):
		"""
		Инициализация GitUpdater.

		Args:
			repo_url (str): URL репозитория GitHub
			local_path (str): Путь для локальной копии 
			branch (str): Название ветки для отслеживания
			update_interval (int): Интервал проверки обновлений в секундах

		Returns:
			None
		"""
		self.repo_url = repo_url
		self.local_path = Path(local_path)
		self.branch = branch
		self.update_interval = update_interval
		self.repo = None
		
	def init_repo(self):
		"""Инициализация локального репозитория"""
		if not self.local_path.exists():
			logger.info("Клонирование репозитория")
			self.repo = git.Repo.clone_from(
				self.repo_url,
				self.local_path,
				branch=self.branch,
				single_branch=True
			)
			
		else:
			logger.info("Подключение к существующему репозиторию")
			self.repo = git.Repo(self.local_path)	

	def reapply_services(self, origin):
		origin.pull()
		logger.info("Обнаружены изменения: получено обновление. Перезапуск сервисов...")
		subprocess.run(['systemclt', 'daemon-reload'])
		subprocess.run(['systemctl', 'restart', 'piworker.service'])
		subprocess.run(['systemctl', 'restart', 'rpi-updater.service'])
		sys.exit(0)

	def check_and_update(self):
		try:
			origin = self.repo.remotes.origin
			origin.fetch()

			if origin.refs[self.branch].commit != self.repo.active_branch.commit:
				self.reapply_services(origin)
		except git.exc.GitCommandError as e:
			logger.error(f"Ошибка Git: {e}")
		except Exception as e:
			logger.error(f"Ошибка: {e}")
	
	def run(self):
		"""Запуск мониторинга обновлений"""
		self.init_repo()

		while True:
			self.check_and_update()
			time.sleep(self.update_interval)	


if __name__ == "__main__":
	updater = GitUpdater(
		repo_url=REPO_PATH,
		local_path=f"/home/{username}/rpi",
		branch="rpi",
		update_interval=180,
	)
	updater.run()
