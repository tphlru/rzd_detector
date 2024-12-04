import time
import subprocess
import sys
import git
from pathlib import Path
import logging
import os
import pwd
import zipfile

from piworker import get_current_device
from pre_start import pre_start

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler('app.log'),
		logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)


REPO_PATH = 'https://github.com/tphlru/rzd_detector.git'
username = get_current_device() or pwd.getpwuid(os.getuid()).pw_name


def extract_zip(zip_file, extract_dir):
	"""
	Извлекает все файлы из zip-архива в указанную директорию.

	Args:
		zip_file (str): Путь к zip-файлу.
		extract_dir (str): Путь к директории, куда будут извлечены файлы.

	Returns:
		None
	"""
	try:
		with zipfile.ZipFile(zip_file, 'r') as zip_ref:
			zip_ref.extractall(extract_dir)
		print(f"Files extracted successfully from {zip_file} to {extract_dir}")
	except FileNotFoundError:
		print(f"File {zip_file} not found")
	except zipfile.BadZipFile:
		print(f"Invalid zip file: {zip_file}")


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
		subprocess.run(f"mv -f /home/{username}/rpi /home/{username}/rpi_old".split())
		if not self.local_path.exists():
			logger.info("Клонирование репозитория")
			self.repo = git.Repo.clone_from(
				self.repo_url,
				f"/home/{username}/rpi",
				branch=self.branch,
				single_branch=True
			)
			
		else:
			logger.info("Подключение к существующему репозиторию")
			self.repo = git.Repo(self.local_path)	

	def reapply_services(self, origin):
		logger.info("Обнаружены изменения: обновление репозитория")
		origin.pull()
		pre_start()
		logger.info("Перезапуск сервисов...")
		subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
		subprocess.run(['sudo', 'systemctl', 'restart', 'piworker.service'])
		subprocess.run(['sudo', 'systemctl', 'restart', 'rpi-updater.service'])
		sys.exit(0)

	def check_and_update(self):
		try:
			logger.info(self.repo.__dict__)
			logger.info(self.repo.active_branch)
			origin = self.repo.remotes.origin
			origin.fetch()

			if origin.refs[self.branch].commit != self.repo.active_branch.commit:
				self.reapply_services(origin)
			else:
				logger.info("Обновление не требуется")
		except git.exc.GitCommandError as e:
			logger.error(f"Ошибка Git: {e}")
		except Exception as e:
			logger.error(f"Ошибка: {e}")
	
	def run(self):
		"""Запуск мониторинга обновлений"""
		self.init_repo()
		logger.info("Запуск мониторинга обновлений")
		while True:
			logger.info("Проверка обновлений...")
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
