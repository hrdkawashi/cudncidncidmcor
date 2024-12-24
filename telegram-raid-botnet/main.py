import locale
import sys

from rich.console import Console

from modules import updater
from modules.settings import Settings
from modules.storages.functions_storage import FunctionsStorage
from modules.storages.sessions_storage import SessionsStorage

console = Console()

console.print("""
  ▄▄▄▄███▄▄▄▄    ▄█     ▄████████    ▄████████  ▄█ 
▄██▀▀▀███▀▀▀██▄ ███    ███    ███   ███    ███ ███ 
███   ███   ███ ███▌   ███    ███   ███    ███ ███▌
███   ███   ███ ███▌  ▄███▄▄▄▄██▀   ███    ███ ███▌
███   ███   ███ ███▌ ▀▀███▀▀▀▀▀   ▀███████████ ███▌
███   ███   ███ ███  ▀███████████   ███    ███ ███ 
███   ███   ███ ███    ███    ███   ███    ███ ███ 
 ▀█   ███   █▀  █▀     ███    ███   ███    █▀  █▀  
                       ███    ███                   
""")

console.print("dev: @auculting")
console.print("Для покупки приватных функций свяжитесь с [link=https://t.me/eucult]https://t.me/eucult\n")

if "UTF-8" not in locale.getlocale():
    console.print("[bold yellow]ПРЕДУПРЕЖДЕНИЕ:[/] У вас не установлена кодировка UTF-8. Ботнет может не работать")

with console.status("Проверка обновлений..."):
    update = updater.check_update()

if update["has_update"]:
    current_commit = update["current_commit"]
    upcoming_commit = update["upcoming_commit"]
    message = update["message"]

    console.print("[bold white]Выпущено новое обновление для ботнета.[/]")

    console.print(
        "[yellow]{current_commit}[/] → [green]{upcoming_commit}[/] : [white]{message}[/]"
        .format(current_commit=current_commit[:8], upcoming_commit=upcoming_commit[:8], message=message)
    )

    install_choice = console.input("[bold white]Установить? (y/n) >> [/]")

    if install_choice == "y":
        updater.update(console)

else:
    console.print("Mirai Botnet v1")

if sys.version_info < (3, 8, 0):
    console.print("\n[red]Ошибка: вы используете устаревшую версию Python. Установите хотя бы Python 3.8.0.")
else:
    if sys.platform == "win32":
        console.print("[yellow]Предупреждение: вы используете Windows. Некоторые функции могут работать некорректно\n")

    settings = Settings()

    sessions_storage = SessionsStorage(
        "sessions",
        settings.api_id,
        settings.api_hash
    )

    functions_storage = FunctionsStorage(
        "functions",
        sessions_storage,
        settings
    )

    console.print("[bold white]Количество аккаунтов: %d[/]" % len(sessions_storage))

    for index, module in enumerate(functions_storage.functions):
        instance, doc = module

        console.print(
            "[bold white][{index}] {doc}[/]"
            .format(index=index + 1, doc=doc)
        )

    while True:
        console.print()

        try:
            choice = console.input(
                "[bold white]>> [/]"
            )

            while not choice.isdigit():
                choice = console.input(
                    "[bold white]>> [/]"
                )
        except KeyboardInterrupt:
            console.print("[bold white]До свидания![/]")
            break

        else:
            choice = int(choice) - 1

        try:
            functions_storage.execute(choice)
        except KeyboardInterrupt:
            pass