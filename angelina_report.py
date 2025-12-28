import pandas as pd
import glob
import os

# Находим все файлы, соответствующие шаблону
files = glob.glob("Transaction-*.xlsx")

if not files:
    print("❌ Нет файлов по шаблону 'Transaction-*.xlsx' в текущей директории.")
    exit()

# Обрабатываем каждый файл
for file_path in sorted(files):
    print(f"\n📄 Обработка файла: {os.path.basename(file_path)}")
    print("-" * 60)

    try:
        # Читаем Excel без заголовков (как в твоих файлах)
        df = pd.read_excel(file_path, header=None, engine='openpyxl')

        # Ожидаем минимум 8 колонок (статус — индекс 6, сумма — индекс 7)
        if df.shape[1] < 8:
            print("⚠️  Файл имеет меньше 8 колонок — пропускаем.")
            continue

        statuses = df.iloc[:, 6]  # Статус
        amounts = df.iloc[:, 7]   # Сумма

        # Инициализация счётчиков
        report = {
            'CAPTURED': {'count': 0, 'amount': 0.0},
            'CANCELLED': {'count': 0, 'amount': 0.0},
            'DECLINED': {'count': 0, 'amount': 0.0},
            'REFUNDED': {'count': 0, 'amount': 0.0},
            'ERROR': {'count': 0, 'amount': 0.0},
        }

        # Подсчёт
        for status, amount in zip(statuses, amounts):
            if pd.isna(status) or pd.isna(amount):
                continue
            status = str(status).strip().upper()
            if status in report:
                report[status]['count'] += 1
                try:
                    report[status]['amount'] += float(amount)
                except (ValueError, TypeError):
                    continue  # пропускаем некорректные суммы

        # Форматирование суммы по-русски: 1 234 567,89
        def fmt_rub(value):
            return f"{value:,.2f}".replace(",", " ").replace(".", ",")

        # Вывод
        print('=== Результаты анализа ===')
        print(f"- Успешных транзакций (CAPTURED): {report['CAPTURED']['count']} шт на сумму {fmt_rub(report['CAPTURED']['amount'])} RUB")
        print(f"- Неоплаченных транзакций (CANCELLED): {report['CANCELLED']['count']} шт на сумму {fmt_rub(report['CANCELLED']['amount'])} RUB")
        print(f"- Отклоненных транзакций (DECLINED): {report['DECLINED']['count']} шт на сумму {fmt_rub(report['DECLINED']['amount'])} RUB")
        print(f"- Ошибочных транзакций (ERROR): {report['ERROR']['count']} шт на сумму {fmt_rub(report['ERROR']['amount'])} RUB")
        print(f"- Возвраты (REFUNDED): {report['REFUNDED']['count']} шт на сумму {fmt_rub(report['REFUNDED']['amount'])} RUB")

    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")

print("\n✅ Обработка завершена.")