import time
import subprocess
import git

REPO_PATH = 'https://github.com/tphlru/rzd_detector.git'
WORKER_SERVICE = 'piworker'


def check_updates():
    repo = git.Repo(REPO_PATH)
    origin = repo.remotes.origin
    
    current = repo.head.commit
    origin.fetch()
    
    if current != repo.head.commit:
        subprocess.run(['systemctl', 'stop', WORKER_SERVICE])
        origin.pull()
        subprocess.run(['systemctl', 'start', WORKER_SERVICE])


while True:
    check_updates()
    time.sleep(300)  # 5 минут
