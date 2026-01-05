import pandas as pd
from pathlib import Path

file_path = "OREC266246732627013632.csv"

if not Path(file_path).exists():
    print(f"Файл {file_path} не найден.")
    exit(1)

# Читаем CSV без заголовков, с точным указанием разделителя
df = pd.read_csv(
    file_path,
    sep=";",
    header=None,
    names=["payment_id", "type", "amount", "currency", "fee", "fee_currency", "status", "timestamp"],
    dtype=str  # читаем всё как строки сначала
)

# Преобразуем сумму в числовой формат (заменяем ',' → '.', если нужно — но у тебя точка)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# Считаем общее количество строк (транзакций)
total_transactions = len(df)

# Фильтруем только CAPTURED и числовые суммы
successful = df[
    (df["status"] == "CAPTURED") &
    df["amount"].notna()
]

successful_count = len(successful)
total_amount = successful["amount"].sum()
success_rate = (successful_count / total_transactions * 100) if total_transactions > 0 else 0

# Вывод
print("\n=== АНАЛИЗ CSV-ФАЙЛА ===")
print(f"Всего транзакций: {total_transactions}")
print(f"Успешных транзакций: {successful_count}")
print(f"Success Rate: {success_rate:.2f}%")
print(f"Оборот (CAPTURED): {total_amount:,.2f} RUB")