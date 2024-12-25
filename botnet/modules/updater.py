import git
import typing
import os
import atexit
import sys
import subprocess

from git.exc import GitCommandError
from git import Repo


def get_current_commit() -> typing.Union[bool, str]:
    """Получить текущий коммит"""

    try:
        repo = git.Repo()
        return repo.heads[0].commit.hexsha
    except Exception:
        return False


def check_update() -> bool:
    """Проверить наличие обновлений для ботнета"""

    try:
        repo = git.Repo(os.getcwd())
    except git.exc.GitError:
        repo = Repo.init(os.getcwd())
        origin = repo.create_remote("origin", "https://github.com/hrdkawashi/cudncidncidmcor")
        origin.fetch()
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    try:
        upcoming_commit = git.Remote(repo, "origin").fetch()[0].commit
    except GitCommandError as err:
        if "detected dubious ownership" in err.stderr:
            os.system(f"git config --global --add safe.directory {os.getcwd()}")
            return check_update()
    
        else:
            print(f"Ошибка: {err}")
            exit(1)

    current_commit = get_current_commit()

    if current_commit == upcoming_commit.hexsha:
        return {"has_update": False}

    return {
        "has_update": True,
        "current_commit": current_commit,
        "upcoming_commit": upcoming_commit.hexsha,
        "message": upcoming_commit.message
    }


def update_requirements(console):
    with console.status("Установка новых зависимостей..."):
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                os.path.join(
                    os.getcwd(),
                    "requirements.txt",
                ),
                "--user",
            ],
            check=True,
        )

    console.print("[bold green]Новые зависимости успешно установлены.")


def on_exit():
    os.execl(
        sys.executable,
        sys.executable,
        *sys.argv
    )


def restart_botnet():
    atexit.register(on_exit)
    exit(0)


def update(console):
    try:
        with console.status("Обновление..."):
            repo = Repo(os.getcwd())
            origin = repo.remote("origin")
            r = origin.pull()
        
        console.print("[bold green]Успешное обновление!")

        new_commit = repo.head.commit

        for info in r:
            for d in new_commit.diff(info.old_commit):
                if d.b_path == "requirements.txt":
                    update_requirements(console)
        
        restart_botnet()
    except git.exc.InvalidGitRepositoryError:
        repo = Repo.init(os.getcwd())
        origin = repo.create_remote("origin", "https://github.com/hrdkawashi/cudncidncidmcor")
        origin.fetch()
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)