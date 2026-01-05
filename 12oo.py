import pandas as pd
import glob
from pathlib import Path
from datetime import datetime, timezone, timedelta

# === Настройка временной зоны Москвы ===
MOSCOW_TZ = timezone(timedelta(hours=3))

# === Собираем все подходящие Excel-файлы ===
files = glob.glob("Transaction-List-Date_*.xlsx")

if not files:
    print("❌ Не найдено файлов вида Transaction-List-Date_*.xlsx")
    exit(1)

print(f"📁 Найдено файлов: {len(files)}")
for f in files:
    print(f" - {f}")

total_count = 0

for file in files:
    try:
        df = pd.read_excel(file, header=None)

        if df.empty:
            continue

        # Пропускаем строку "Transactions", если она есть
        if str(df.iloc[0, 0]).strip() == "Transactions":
            df = df.iloc[1:].reset_index(drop=True)

        # Проверяем наличие колонки "Created" (индекс 2)
        if df.shape[1] < 3:
            print(f"⚠️ Пропущен {file}: недостаточно колонок")
            continue

        # Считаем транзакции до 12:00 по Москве
        count = 0
        for _, row in df.iterrows():
            ts_str = str(row[2]).strip()
            if not ts_str or ts_str == "nan":
                continue
            try:
                dt_utc = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                dt_moscow = dt_utc.astimezone(MOSCOW_TZ)
                if dt_moscow.hour < 12:
                    count += 1
            except Exception:
                continue  # пропускаем битые строки

        total_count += count
        print(f"✅ {Path(file).name}: {count} транзакций до 12:00")

    except Exception as e:
        print(f"❌ Ошибка при обработке {file}: {e}")

# === Результат ===
print("\n" + "="*50)
print(f"📊 Всего транзакций до 12:00 по Москве: {total_count}")
print("="*50)