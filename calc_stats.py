import pandas as pd
import glob
from pathlib import Path

# Находим все файлы по шаблону
files = glob.glob("Transaction-*.xlsx")

if not files:
    print("Файлы не найдены. Убедитесь, что в папке есть файлы, начинающиеся с 'Transaction-' и имеющие расширение .xlsx")
    print("Доступные файлы:")
    for f in Path('.').glob('*'):
        if f.is_file():
            print(f"- {f.name}")
    exit(1)

print(f"Найдено файлов: {len(files)}")
for i, file in enumerate(files, 1):
    print(f"{i}. {file}")

all_dfs = []
for file in files:
    try:
        print(f"Обработка: {Path(file).name}")
        df = pd.read_excel(file, header=None)
        df.dropna(how='all', inplace=True)
        if not df.empty:
            all_dfs.append(df)
    except Exception as e:
        print(f"Ошибка при обработке {file}: {e}")

if not all_dfs:
    print("Нет данных для обработки.")
    exit(1)

# Объединяем
full_df = pd.concat(all_dfs, ignore_index=True)

# Определяем колонки вручную (на основе структуры)
# Колонка 6 — это статус (начинаем с 0)
# Колонка 7 — сумма в RUB
full_df.columns = [f'col_{i}' for i in range(full_df.shape[1])]

status_col = full_df['col_6']
amount_col = full_df['col_7']

# Только строки с CAPTURED и числовыми суммами
valid = (status_col == 'CAPTURED') & pd.to_numeric(amount_col, errors='coerce').notna()
successful = full_df[valid]
total_amount = pd.to_numeric(successful['col_7']).sum()
total_operations = len(full_df)
successful_operations = len(successful)
success_rate = successful_operations / total_operations * 100

print("\n=== Результаты анализа ===")
print(f"Всего операций: {total_operations}")
print(f"Успешных операций: {successful_operations}")
print(f"Success Rate: {success_rate:.2f}%")
print(f"Оборот за сутки: {total_amount:,.2f} RUB")