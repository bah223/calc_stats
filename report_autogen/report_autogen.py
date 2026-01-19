import csv
import re
from pathlib import Path
from typing import List, Dict, Union, Optional

def parse_number(val: str) -> int:
    """Преобразует строку вида '2,345' в целое число. Пустые строки → 0."""
    if not val or val.strip() == '':
        return 0
    # Убираем запятые и пробелы
    cleaned = re.sub(r'[,\s]', '', val.strip())
    try:
        return int(cleaned)
    except ValueError:
        return 0

def calculate_change(old: int, new: int) -> Optional[Dict[str, Union[str, float, int]]]:
    """Возвращает описание изменения или None, если old == new == 0."""
    if old == 0 and new == 0:
        return None

    if old == 0 and new > 0:
        return {
            'type': 'growth_new',
            'desc': f'рост (0 → {new})'
        }
    elif old > 0 and new == 0:
        return {
            'type': 'drop_gone',
            'desc': f'сокращение на 100% ({old} → 0)'
        }
    else:
        diff = new - old
        percent = (diff / old) * 100 if old != 0 else 0
        if percent >= 0:
            desc = f'рост на {percent:,.2f} ({old} → {new})'.replace('.', ',')
        else:
            desc = f'сокращение на {abs(percent):,.2f} ({old} → {new})'.replace('.', ',')
        return {
            'type': 'change',
            'percent': percent,
            'desc': desc
        }

def is_in_watchlist(account: str, id_val: str, watchlist: List[str]) -> bool:
    """Проверяет, есть ли аккаунт или ID в watchlist."""
    if id_val in watchlist:
        return True
    if account in watchlist:
        return True
    # Поддержка частичного совпадения по названию (например, "все аккаунты")
    for w in watchlist:
        if w in account:
            return True
    return False

def generate_traffic_report(
    csv_file: str,
    duty_officer: str,
    report_time: str,
    base_date: str,
    current_date: str,
    watchlist: List[str]
):
    file_path = Path(csv_file)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {csv_file}")

    with open(file_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("Дежурный [Имя]. В [время] был сделан отчет за [дата]. Изменений трафика, превышающих пороги (рост ≥50% или падение ≥30%), не выявлено. Все проверили, трафик не поменялся.")
        return

    # Определяем имена колонок дат
    fieldnames = reader.fieldnames or []
    if len(fieldnames) < 4:
        raise ValueError("Ожидалось минимум 4 колонки: Аккаунт, ID, [Базовая дата], [Текущая дата]")

    col_account = 'Аккаунт'
    col_id = 'ID'
    col_base = fieldnames[-2]   # предпоследняя — базовая
    col_current = fieldnames[-1]  # последняя — текущая

    report_lines = []
    for row in rows:
        account = row.get(col_account, '').strip()
        id_val = row.get(col_id, '').strip()
        base_val = parse_number(row.get(col_base, ''))
        current_val = parse_number(row.get(col_current, ''))

        # Режим B: только из watchlist
        if not is_in_watchlist(account, id_val, watchlist):
            continue

        change_info = calculate_change(base_val, current_val)
        if change_info is None:
            # Оба нуля — всё равно включаем для видимости
            diff_abs = 0
            desc = "нет трафика (0 → 0)"
        else:
            diff_abs = abs(current_val - base_val)
            desc = change_info['desc']

        prefix = f"{id_val} {account}" if id_val else account
        line = f"{prefix} — {desc}"
        report_lines.append((diff_abs, line))

    # Сортировка по модулю разницы (по убыванию)
    report_lines.sort(key=lambda x: x[0], reverse=True)
    final_lines = [line for _, line in report_lines]

    # Формируем заголовок
    time_label = "ночной" if report_time == "00:00" else "дневной"
    header = f"Дежурный {duty_officer}. В {report_time} был сделан отчет за {current_date}, выявлены изменения трафика по сравнению с {base_date} на {report_time}:"

    if not final_lines:
        fallback_msg = f"Дежурный {duty_officer}. В {report_time} был сделан отчет за {current_date}. Изменений трафика, превышающих пороги (рост ≥50% или падение ≥30%), не выявлено. Все проверили, трафик не поменялся."
        print(fallback_msg)
    else:
        print(header)
        for line in final_lines:
            print(line)

# Пример использования (можно закомментировать при интеграции)
if __name__ == "__main__":
    generate_traffic_report(
        csv_file="Sheet1.csv",
        duty_officer="Турченко",
        report_time="12:00",
        base_date="06.01.2026",
        current_date="13.01.2026",
        watchlist=[
            "3953", "3954", "3956",
            "AA195783946319400960",
            "PAY365/ZT/Aghanim Inc. (все аккаунты: МТС, Билайн)"
        ]
    )