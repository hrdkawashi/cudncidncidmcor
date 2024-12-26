import locale
import sys
from rich.align import Align
from rich.console import Console
from modules import updater
from modules.settings import Settings
from modules.storages.functions_storage import FunctionsStorage
from modules.storages.sessions_storage import SessionsStorage

console = Console()

# ASCII-баннер
header = """
  ▄▄▄▄███▄▄▄▄    ▄█     ▄████████    ▄████████  ▄█ 
▄██▀▀▀███▀▀▀██▄ ███    ███    ███   ███    ███ ███ 
███   ███   ███ ███▌   ███    ███   ███    ███ ███▌
███   ███   ███ ███▌  ▄███▄▄▄▄██▀   ███    ███ ███▌
███   ███   ███ ███▌ ▀▀███▀▀▀▀▀   ▀███████████ ███▌
███   ███   ███ ███  ▀███████████   ███    ███ ███ 
███   ███   ███ ███    ███    ███   ███    ███ ███ 
 ▀█   ███   █▀  █▀     ███    ███   ███    █▀  █▀  
                       ███    ███                   
"""
centered_header = Align.center(header)
console.print(centered_header)

console.print("[bold green]Mirai Botnet v1[/]", justify="center")
console.print(
    "Для покупки приватных функций свяжитесь с [link=https://t.me/eucult]https://t.me/eucult",
    justify="center"
)

if "UTF-8" not in locale.getlocale():
    console.print("[bold yellow]ПРЕДУПРЕЖДЕНИЕ:[/] У вас не установлена кодировка UTF-8. Ботнет может не работать")

# Проверка обновлений
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

    if install_choice.lower() == "y":
        updater.update(console)

if sys.version_info < (3, 8, 0):
    console.print("\n[red]Ошибка: вы используете устаревшую версию Python. Установите хотя бы Python 3.8.0.")
    sys.exit(1)

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

# Формируем список функций из других скриптов
function_list = []
for index, (function_name, docstring) in enumerate(functions_storage.functions):
    function_list.append(f"[{index + 1}] {docstring}")

# Подготовка таблицы для отображения
num_columns = 3
rows = [function_list[i:i + num_columns] for i in range(0, len(function_list), num_columns)]

# Границы таблицы
top_border = "╔" + "═" * 34 + "╦" + "═" * 34 + "╦" + "═" * 34 + "╗"
bottom_border = "╚" + "═" * 34 + "╩" + "═" * 34 + "╩" + "═" * 34 + "╝"

# Построение таблицы
table_lines = [top_border]
for row in rows:
    row_line = "║"
    for item in row:
        row_line += f" {item:<32}║"  # Выравнивание по ширине 34
    # Добавляем пустые ячейки, если элементов в строке меньше колонок
    for _ in range(num_columns - len(row)):
        row_line += f" {'':<32}║"
    table_lines.append(row_line)
# Добавляем нижнюю границу
table_lines.append(bottom_border)

# Отображение таблицы
centered_menu = Align.center("\n".join(table_lines))
console.print(centered_menu)

# Основной цикл взаимодействия
while True:
    console.print()

    try:
        choice = console.input("[bold white]>> [/]")
        while not choice.isdigit():
            choice = console.input("[bold white]>> [/]")

        choice = int(choice) - 1  # Преобразуем к 0-based индексу

        functions_storage.execute(choice)

    except IndexError:
        console.print("[bold red]Неверный выбор. Попробуйте снова.[/]")
    except KeyboardInterrupt:
        console.print("\n[bold white]До свидания![/]")
        break
    except Exception as e:
        console.print(f"[bold red]Ошибка:[/] {e}")