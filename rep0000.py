import pandas as pd
import os
import sys
import re

SPECIAL_MERCHANTS = [
    ("Carusell/WhiteBird", "AA195783946319400960"),
    ("MyGames MENA FZ LLC", "AA254873800273182720"),
    ("Pagsmile Limited", "AA257439891205799936"),
    ("AO T-Bank (ПЛ-ЗЕС-КА-1-12052025 от 13.05.2025)", ""),
    ("SWOOSHTRANSFER LTD", "AA237116718312734720")
]

# Список ID, для которых не нужно показывать ID (и которые нужно показывать в полном отчёте отдельно)
HIDE_IDS = ['4065', '4066', '4067', '4068', '4069', '4085', '4116',
            '4117', '4119', '4246', '4247', '4252', '4255', '4258',
            '4261', '4268', '4271', '4273']

def get_special_merchant_data():
    """Запрашивает у пользователя данные для специальных аккаунтов"""
    print("\n" + "="*80)
    print("ВВОД ДАННЫХ ДЛЯ СПЕЦИАЛЬНЫХ АККАУНТОВ".center(80))
    print("="*80)
    print("Для каждого аккаунта введите две цифры (date1 и date2) через пробел")
    print("Пример: 1000 1500\n")
    
    special_data = {}
    
    for merchant_name, merchant_id in SPECIAL_MERCHANTS:
        while True:
            try:
                display_id = f" ({merchant_id})" if merchant_id else ""
                user_input = input(f"{merchant_name}{display_id}: ").strip()
                
                if not user_input:
                    print("  ⚠️ Пожалуйста, введите два числа через пробел")
                    continue
                
                parts = user_input.split()
                if len(parts) != 2:
                    print("  ⚠️ Введите ровно две цифры через пробел")
                    continue
                
                date1 = int(parts[0])
                date2 = int(parts[1])
                
                special_data[merchant_name] = {
                    'date1': date1,
                    'date2': date2,
                    'id': merchant_id
                }
                
                # Рассчитываем процентное изменение
                if date1 == 0 and date2 == 0:
                    change_str = "0 → 0 (без изменений)"
                elif date1 == 0:
                    change_str = f"новый поток (0 → {date2})"
                elif date2 == 0:
                    change_str = f"-100.00% (закрыт) ({date1} → 0)"
                else:
                    pct = ((date2 - date1) / date1) * 100
                    emoji = "📈" if pct >= 0 else "📉"
                    sign = "+" if pct >= 0 else ""
                    change_str = f"{emoji} {sign}{pct:.2f}% ({date1} → {date2})"
                
                print(f"  ✓ {change_str}")
                break
                
            except ValueError:
                print("  ⚠️ Ошибка: введите числовые значения")
            except Exception as e:
                print(f"  ⚠️ Ошибка ввода: {e}")
    
    print("\n" + "="*80 + "\n")
    return special_data

def calculate_change(old, new):
    if old == 0 and new == 0:
        return "⚪️ 0 → 0"
    elif old == 0:
        return "🟢 +∞% (новый поток)"
    elif new == 0:
        return "🔴 -100.00%"
    else:
        pct = (new - old) / old * 100
        emoji = "🟢" if pct >= 0 else "🔴"
        sign = "+" if pct >= 0 else ""
        return f"{emoji} {sign}{pct:.2f}%"

def normalize_df(df, source_type, excluded_merchant_ids=None, keep_zero_rows=False):
    if excluded_merchant_ids is None:
        excluded_merchant_ids = []
    """Приводит df к merchant_name, date1, date2"""
    print(f"\nОбработка файла типа: {source_type}")
    print("Доступные колонки:", list(df.columns))
    
    # Выводим информацию о типах данных в колонках
    print("\nТипы данных в колонках:")
    for col in df.columns:
        print(f"- {col}: {df[col].dtype}, пример: {df[col].iloc[0] if len(df) > 0 else 'нет данных'}")
    
    # Ищем колонки с ID и названиями мерчантов
    merchant_col = None
    id_col = None
    merchant_keywords = ['merchant', 'мерчант', 'название', 'группа', 'имя', 'name', 'магазин', 'shop', 'компания']
    id_keywords = ['id', 'код', 'номер']
    
    # Сначала ищем ID колонку
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in id_keywords) and 'id' in col_lower:
            id_col = col
            break
    
    # Ищем колонку с названием мерчанта
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in merchant_keywords) and 'id' not in col_lower:
            merchant_col = col
            break
    
    # Если не нашли по ключевым словам, ищем первую текстовую колонку
    if merchant_col is None:
        for col in df.columns:
            if df[col].dtype == 'object' and len(df[col].dropna()) > 0 and col != id_col:
                sample = str(df[col].iloc[0]).lower()
                if not any(x in sample for x in ['date', 'дата', 'timestamp']) and len(sample) > 3:
                    merchant_col = col
                    break
    
    # Если не нашли ID, берем первую числовую колонку
    if id_col is None:
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                id_col = col
                break
        if id_col is None and len(df.columns) > 0:
            id_col = df.columns[0]  # Берем первую колонку, если не нашли подходящую
    
    # Если не нашли мерчант, берем вторую колонку
    if merchant_col is None and len(df.columns) > 1:
        merchant_col = df.columns[1] if df.columns[1] != id_col else df.columns[0]
    elif merchant_col is None:
        merchant_col = df.columns[0]
    
    # Очищаем названия мерчантов и ID
    df[merchant_col] = df[merchant_col].astype(str).str.strip().str.replace('"', '').str.strip()
    if id_col != merchant_col:
        df[id_col] = df[id_col].astype(str).str.strip().str.replace('"', '').str.strip()
    
    # Удаляем пустые строки
    df = df[df[merchant_col] != '']
    df = df[df[merchant_col].str.lower() != 'nan']
    
    # Примечание: не удаляем строки с excluded_merchant_ids здесь —
    # они будут обрабатываться и отображаться в полном отчёте (process_files соберёт их отдельно).
    
    # Объединяем ID и название мерчанта, если это разные колонки
    # Исключение для определенных мерчантов, где ID не нужен
    if id_col != merchant_col and id_col in df.columns:
        # Используем глобальный список HIDE_IDS
        
        # Функция для форматирования ID и названия
        def format_merchant(row):
            merchant_id = str(row[id_col]).strip()
            merchant_name = str(row[merchant_col]).strip()
            
            # Проверяем, нужно ли скрывать ID для этого мерчан��а
            if any(hide_id in merchant_id for hide_id in HIDE_IDS):
                return merchant_name
            
            # Проверяем, есть ли уже ID в названии
            if merchant_id and not merchant_name.startswith(merchant_id):
                return f"{merchant_id} {merchant_name}"
            return merchant_name
        
        # Применяем форматирование
        df[merchant_col] = df.apply(format_merchant, axis=1)
    
    # Сохраняем оригинальный ID в отдельной колонке, чтобы потом можно было показать скрытые ID в полном отчёте
    if id_col in df.columns:
        df['merchant_id'] = df[id_col].astype(str).str.strip()
    else:
        df['merchant_id'] = ''
    
    # Удаляем дубликаты по названию мерчанта
    df = df.drop_duplicates(subset=[merchant_col])
    
    # Берем первые две числовые колонки для значений
    numeric_cols = []
    
    # Пытаемся найти числовые колонки
    numeric_cols = []
    
    # Сначала ищем колонки, которые выглядят как даты или значения
    possible_value_cols = []
    for col in df.columns:
        col_str = str(col).lower()
        # Пропускаем колонки с ID и названиями
        if any(x in col_str for x in ['id', 'name', 'название', 'мерчант', 'группа']):
            continue
        # Пробуем преобразовать значения в числа
        try:
            # Пробуем преобразовать в число, заменяя пробелы и запятые
            sample = df[col].dropna().head(10)
            if len(sample) > 0:
                # Пробуем преобразовать в число
                pd.to_numeric(sample.astype(str).str.replace(' ', '').str.replace(',', '.'), errors='raise')
                possible_value_cols.append(col)
        except:
            continue
    
    # Если нашли хотя бы 2 числовые колонки
    if len(possible_value_cols) >= 2:
        numeric_cols = possible_value_cols[:2]
    else:
        # Берем все колонки, кроме merchant_col
        other_cols = [col for col in df.columns if col != merchant_col]
        numeric_cols = other_cols[:2]
    
    if len(numeric_cols) < 2:
        print("\nОшибка: Не удалось определить числовые колонки.")
        print("Доступные колонки:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i}. {col} (тип: {df[col].dtype}, пример: {str(df[col].iloc[0])[:50]}...")
        raise ValueError("Нужно как минимум 2 колонки с числовыми данными.")
    
    # Преобразуем выбранные колонки в числа
    for col in numeric_cols:
        try:
            # Сначала преобразуем в строку, если это еще не строка
            if not pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype(str)
            
            # Очищаем и преобразуем в числа
            df[col] = (
                df[col].str.strip()  # Удаляем пробелы по краям
                .str.replace(r'[^\d,-]', '', regex=True)  # Оставляем только цифры, запятые и минусы
                .str.replace(',', '.')  # Меняем запятые на точки
                .replace('', '0')  # Пустые строки в 0
                .replace('nan', '0')  # NaN в 0
                .astype(float)  # Преобразуем в float
                .fillna(0)  # Заполняем оставшиеся NaN нулями
                .astype(int)  # Преобразуем в целые числа
            )
            
            # Выводим отладочную информацию
            print(f"\nКолонка {col} преобразована. Примеры значений:")
            print(df[col].head().to_string())
            
        except Exception as e:
            print(f"\nОшибка при преобразовании колонки '{col}': {str(e)}")
            print(f"Пример значения: {df[col].iloc[0] if len(df) > 0 else 'нет данных'}")
            df[col] = 0  # Заменяем на 0 в случае ошибки
    
    print(f"\nИспользуем колонки:")
    print(f"- Мерчанты: {merchant_col}")
    print(f"- Значение 1: {numeric_cols[0]}")
    print(f"- Значение 2: {numeric_cols[1]}")
    
    # Приводим к нужному формату
    result = df.rename(columns={
        merchant_col: "merchant_name",
        numeric_cols[0]: "date1",
        numeric_cols[1]: "date2"
    })
    
    # Очищаем и преобразуем данные
    result = result[["merchant_name", "date1", "date2", "merchant_id"]].copy()
    
    # Удаляем строки, где оба значения нулевые (по умолчанию).
    # Если нужен полный дамп для аналитики — передайте keep_zero_rows=True
    if not keep_zero_rows:
        result = result[(result["date1"] != 0) | (result["date2"] != 0)]
    
    # Сортируем по убыванию разницы между date2 и date1
    result = result.assign(diff=result["date2"] - result["date1"])
    result = result.sort_values(by="diff", ascending=False)
    result = result.drop(columns=["diff"])
    
    # Преобразуем числовые колонки, заменяя нечисловые значения на 0
    for col in ["date1", "date2"]:
        result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0).astype(int)
    
    # Удаляем строки, где оба значения равны 0 (если не требуется сохранять их)
    if not keep_zero_rows:
        result = result[(result["date1"] != 0) | (result["date2"] != 0)]
    
    print(f"Успешно обработано {len(result)} записей")
    return result

def classify_file(filename):
    if "aggregated_data" in filename:
        return "ВП"
    elif "19_00_00" in filename:
        return "Выплаты KZT"
    elif "20_59_00" in filename:
        return "F.A.T. Pagsmile"
    elif "00_00_00" in filename:
        return "F.A.T. Не-Pagsmile"
    else:
        return "Прочее"

def process_files(files, excluded_merchant_ids=None):
    """Обрабатывает все файлы и возвращает список мерчантов с изменениями"""
    merchant_data = {}
    excluded_data = {}  # Для отслеживания исключённых аккаунтов
    empty_id_data = {}  # Для аккаунтов без ID
    hidden_ids_data = {}  # Для аккаунтов из HIDE_IDS
    
    if excluded_merchant_ids is None:
        excluded_merchant_ids = []
    
    for filename, df in files:
        print(f"\nОбработка файла: {filename}")
        for _, row in df.iterrows():
            merchant = str(row['merchant_name']).strip()
            old_val = row.get('date1', 0)
            new_val = row.get('date2', 0)
            
            # Пропускаем пустые или некорректные значения
            if not merchant or merchant.lower() in ['nan', 'none', '']:
                continue
            
            # Берём ID из отдельной колонки, если она есть (normalize_df добавляет её)
            merchant_id = str(row.get('merchant_id', '')).strip()
            # Отслеживаем исключённые аккаунты
            if merchant_id and merchant_id in excluded_merchant_ids:
                    if merchant not in excluded_data:
                        excluded_data[merchant] = {'old': 0, 'new': 0}
                    try:
                        old_val = int(float(old_val)) if pd.notna(old_val) else 0
                        new_val = int(float(new_val)) if pd.notna(new_val) else 0
                    except (ValueError, TypeError):
                        old_val = 0
                        new_val = 0
                    excluded_data[merchant]['old'] += old_val
                    excluded_data[merchant]['new'] += new_val
                    continue
            
            # Проверяем аккаунты без ID (нет merchant_id и название не начинается с 'AA')
            if not merchant_id and not merchant.startswith('AA'):
                if merchant not in empty_id_data:
                    empty_id_data[merchant] = {'old': 0, 'new': 0}
                try:
                    old_val = int(float(old_val)) if pd.notna(old_val) else 0
                    new_val = int(float(new_val)) if pd.notna(new_val) else 0
                except (ValueError, TypeError):
                    old_val = 0
                    new_val = 0
                empty_id_data[merchant]['old'] += old_val
                empty_id_data[merchant]['new'] += new_val
                continue
                
            # Приводим к целым числам
            try:
                old_val = int(float(old_val)) if pd.notna(old_val) else 0
                new_val = int(float(new_val)) if pd.notna(new_val) else 0
            except (ValueError, TypeError):
                old_val = 0
                new_val = 0
            
            # Раньше мы пропускали записи, где оба значения нулевые.
            # Теперь сохраняем их для полной аналитики (фильтрация в основном отчете останется).
            # if old_val == 0 and new_val == 0:
            #     continue

            # Собираем отдельно аккаунты, для которых скрываем ID (HIDE_IDS)
            if merchant_id and merchant_id in HIDE_IDS:
                if merchant not in hidden_ids_data:
                    hidden_ids_data[merchant] = {'old': 0, 'new': 0, 'id': merchant_id}
                try:
                    old_val = int(float(old_val)) if pd.notna(old_val) else 0
                    new_val = int(float(new_val)) if pd.notna(new_val) else 0
                except (ValueError, TypeError):
                    old_val = 0
                    new_val = 0
                hidden_ids_data[merchant]['old'] += old_val
                hidden_ids_data[merchant]['new'] += new_val
                
            if merchant not in merchant_data:
                merchant_data[merchant] = {'old': 0, 'new': 0}
                
            merchant_data[merchant]['old'] += old_val
            merchant_data[merchant]['new'] += new_val
    
    return merchant_data, excluded_data, empty_id_data, hidden_ids_data

def format_change(old_val, new_val):
    """Форматирует изменение в нужном формате"""
    if old_val == 0 and new_val == 0:
        return f"{new_val} шт."
    elif old_val == 0:
        return f"({old_val}→{new_val})"
    elif new_val == 0:
        return f"на 100% ({old_val}→{new_val})"
    else:
        pct = ((new_val - old_val) / old_val) * 100
        return f"на {pct:.1f}% ({old_val}→{new_val})"

def print_full_analytics(merchant_data, special_merchant_data, excluded_data, empty_id_data, hidden_ids_data):
    """Выводит полную аналитику всех аккаунтов без фильтров"""
    print("\n" + "="*80)
    print("ПОЛНАЯ АНАЛИТИКА ДЛЯ АНАЛИЗА (ВСЕ АККАУНТЫ БЕЗ ИСКЛЮЧЕНИЯ)".center(80))
    print("="*80)
    
    # Собираем все данные
    all_data = []
    
    # Добавляем данные из CSV файлов
    for merchant, values in merchant_data.items():
        old_val = values['old']
        new_val = values['new']
        # Включаем также записи с 0→0 для полной аналитики
        if old_val == 0 and new_val == 0:
            pct_change = 0.0
        elif old_val == 0:
            pct_change = float('inf')
        elif new_val == 0:
            pct_change = -100.0
        else:
            pct_change = ((new_val - old_val) / old_val) * 100
        
        all_data.append({
            'name': merchant,
            'old': old_val,
            'new': new_val,
            'pct': pct_change,
            'is_special': False
        })
    
    # Добавляем специальные аккаунты
    if special_merchant_data:
        for merchant_name, data in special_merchant_data.items():
            old_val = data['date1']
            new_val = data['date2']
            merchant_id = data['id']
            # Включаем также 0→0 для специальных аккаунтов
            display_name = f"{merchant_id} {merchant_name}" if merchant_id else merchant_name
            if old_val == 0 and new_val == 0:
                pct_change = 0.0
            elif old_val == 0:
                pct_change = float('inf')
            elif new_val == 0:
                pct_change = -100.0
            else:
                pct_change = ((new_val - old_val) / old_val) * 100
            
            all_data.append({
                'name': display_name,
                'old': old_val,
                'new': new_val,
                'pct': pct_change,
                'is_special': True
            })
    
    if not all_data:
        print("Нет данных для аналитики")
        return
    
    # Сортируем: сначала по убыванию, потом по возрастанию
    increasing_data = [d for d in all_data if d['pct'] > 0 or d['pct'] == float('inf')]
    decreasing_data = [d for d in all_data if d['pct'] < 0]
    stable_data = [d for d in all_data if d['pct'] == 0]
    
    # Сортируем
    increasing_data.sort(key=lambda x: float('-inf') if x['pct'] == float('inf') else x['pct'], reverse=True)
    decreasing_data.sort(key=lambda x: x['pct'])  # По возрастанию (от -100 к 0)
    
    # Выводим рост
    print("\n📈 РОСТ (отсортировано по убыванию %):")
    print("-"*80)
    for item in increasing_data:
        special_mark = " [SPECIAL]" if item['is_special'] else ""
        if item['pct'] == float('inf'):
            print(f"{item['name']} — новый поток (0→{item['new']}){special_mark}")
        else:
            sign = "+" if item['pct'] >= 0 else ""
            print(f"{item['name']} — {sign}{item['pct']:.2f}% ({item['old']}→{item['new']}){special_mark}")
    
    # Выводим падение
    print("\n📉 ПАДЕНИЕ (отсортировано по убыванию %):")
    print("-"*80)
    for item in decreasing_data:
        special_mark = " [SPECIAL]" if item['is_special'] else ""
        if item['pct'] == -100.0:
            print(f"{item['name']} — -100.00% ({item['old']}→0){special_mark}")
        else:
            print(f"{item['name']} — {item['pct']:.2f}% ({item['old']}→{item['new']}){special_mark}")
    
    # Выводим стабильные (если есть)
    if stable_data:
        print("\n⚪️ БЕЗ ИЗМЕНЕНИЙ:")
        print("-"*80)
        for item in stable_data:
            special_mark = " [SPECIAL]" if item['is_special'] else ""
            print(f"{item['name']} — 0.00% ({item['old']}→{item['new']}){special_mark}")
    
    # Выводим исключённые аккаунты
    if excluded_data:
        print("\n🚫 ИСКЛЮЧЁННЫЕ АККАУНТЫ (по ID):")
        print("-"*80)
        excluded_list = []
        for merchant, values in excluded_data.items():
            old_val = values['old']
            new_val = values['new']
            
            if old_val == 0 and new_val == 0:
                pct_change = 0
            elif old_val == 0:
                pct_change = float('inf')
            elif new_val == 0:
                pct_change = -100.0
            else:
                pct_change = ((new_val - old_val) / old_val) * 100
            
            excluded_list.append((merchant, old_val, new_val, pct_change))
        
        # Сортируем по процентному изменению
        excluded_list.sort(key=lambda x: float('-inf') if x[3] == float('inf') else x[3], reverse=True)
        
        for merchant, old_val, new_val, pct_change in excluded_list:
            if pct_change == float('inf'):
                print(f"{merchant} — новый поток (0→{new_val})")
            elif pct_change == -100.0:
                print(f"{merchant} — -100.00% ({old_val}→0)")
            else:
                sign = "+" if pct_change >= 0 else ""
                print(f"{merchant} — {sign}{pct_change:.2f}% ({old_val}→{new_val})")
    
    # Выводим аккаунты, для которых скрываем ID (HIDE_IDS)
    if hidden_ids_data:
        print("\n🔒 АККАУНТЫ С СКРЫТЫМИ ID (не публикуются в основном, показываем для аналитики):")
        print("-"*80)
        hidden_list = []
        for merchant, vals in hidden_ids_data.items():
            old_val = vals.get('old', 0)
            new_val = vals.get('new', 0)
            hid = vals.get('id', '')
            if old_val == 0 and new_val == 0:
                pct_change = 0
            elif old_val == 0:
                pct_change = float('inf')
            elif new_val == 0:
                pct_change = -100.0
            else:
                pct_change = ((new_val - old_val) / old_val) * 100
            hidden_list.append((hid, merchant, old_val, new_val, pct_change))

        # Сортируем
        hidden_list.sort(key=lambda x: float('-inf') if x[4] == float('inf') else x[4], reverse=True)
        for hid, merchant, old_val, new_val, pct_change in hidden_list:
            display_name = f"{hid} {merchant}" if hid else merchant
            if pct_change == float('inf'):
                print(f"{display_name} — новый поток (0→{new_val})")
            elif pct_change == -100.0:
                print(f"{display_name} — -100.00% ({old_val}→0)")
            else:
                sign = "+" if pct_change >= 0 else ""
                print(f"{display_name} — {sign}{pct_change:.2f}% ({old_val}→{new_val})")

    # Выводим аккаунты без ID
    if empty_id_data:
        print("\n⚠️ АККАУНТЫ БЕЗ ID (ID не подтянулся):")
        print("-"*80)
        empty_list = []
        for merchant, values in empty_id_data.items():
            old_val = values['old']
            new_val = values['new']
            
            if old_val == 0 and new_val == 0:
                pct_change = 0
            elif old_val == 0:
                pct_change = float('inf')
            elif new_val == 0:
                pct_change = -100.0
            else:
                pct_change = ((new_val - old_val) / old_val) * 100
            
            empty_list.append((merchant, old_val, new_val, pct_change))
        
        # Сортируем по процентному изменению
        empty_list.sort(key=lambda x: float('-inf') if x[3] == float('inf') else x[3], reverse=True)
        
        for merchant, old_val, new_val, pct_change in empty_list:
            if pct_change == float('inf'):
                print(f"{merchant} — новый поток (0→{new_val})")
            elif pct_change == -100.0:
                print(f"{merchant} — -100.00% ({old_val}→0)")
            else:
                sign = "+" if pct_change >= 0 else ""
                print(f"{merchant} — {sign}{pct_change:.2f}% ({old_val}→{new_val})")
    
    print("\n" + "="*80 + "\n")

def main(folder_path):
    # Список ID мерчантов, которые нужно исключить из отчета
    EXCLUDED_MERCHANT_IDS = [
        "3245", "3240", "3243", "3244", "3239", "3247", "3232",
        "3028", "3234", "3235", "3236", "3233", "3021", "3246"
    ]
    
    # Получаем данные для специальных аккаунтов от пользователя
    special_merchant_data = get_special_merchant_data()
    
    print(f"Обработка файлов в директории: {folder_path}")
    print("-" * 50)
    
    all_files = []
    
    # Собираем все CSV файлы
    file_count = 0
    for filename in os.listdir(folder_path):
        if not filename.endswith(".csv"):
            continue
            
        file_count += 1
        try:
            # Пробуем разные варианты чтения файла
            try:
                # Вариант 1: CSV с запятыми, кавычками и русскими символами
                df = pd.read_csv(
                    os.path.join(folder_path, filename),
                    sep=',',
                    quotechar='"',
                    encoding='utf-8',
                    thousands=' ',
                    decimal=','
                )
            except Exception as e1:
                try:
                    # Вариант 2: CSV с точкой с запятой
                    df = pd.read_csv(
                        os.path.join(folder_path, filename),
                        sep=';',
                        quotechar='"',
                        encoding='utf-8',
                        thousands=' ',
                        decimal=','
                    )
                except Exception as e2:
                    # Вариант 3: Автоопределение параметров
                    df = pd.read_csv(
                        os.path.join(folder_path, filename),
                        engine='python',
                        encoding_errors='replace'
                    )
            
            # Выводим информацию о загруженных данных
            print(f"\nФайл: {filename}")
            print("Первые 3 строки данных:")
            print(df.head(3).to_string())
            print("\nКолонки:", df.columns.tolist())
            
            file_type = classify_file(filename)
            # Сохраняем также строки с 0→0 для последующей полной аналитики
            normalized_df = normalize_df(df, file_type, EXCLUDED_MERCHANT_IDS, keep_zero_rows=True)
            all_files.append((filename, normalized_df))
            print(f"Успешно обработан файл: {filename} ({file_type})")
            
        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    if file_count == 0:
        print("Не найдено CSV файлов для обработки.")
        return
    
    # Обрабатываем все файлы вместе
    merchant_data, excluded_data, empty_id_data, hidden_ids_data = process_files(all_files, EXCLUDED_MERCHANT_IDS)
    
    if not (merchant_data or excluded_data or empty_id_data or hidden_ids_data or special_merchant_data):
        print("\nНе найдено данных для отображения. Проверьте входные файлы.")
        return
    
    # Выводим полную аналитику для анализа
    print_full_analytics(merchant_data, special_merchant_data, excluded_data, empty_id_data, hidden_ids_data)
    
    # Разделяем на категории
    increasing = []
    decreasing = []
    stable = []
    
    for merchant, values in merchant_data.items():
        old_val = values['old']
        new_val = values['new']
        
        # Пропускаем нулевые значения
        if old_val == 0 and new_val == 0:
            continue
            
        # Рассчитываем процентное изменение
        if old_val == 0 and new_val > 0:  # Новый мерчант
            increasing.append((merchant, old_val, new_val))
        elif new_val == 0:  # Удаленный мерчант
            decreasing.append((merchant, old_val, new_val))
        elif old_val > 0:
            pct_change = ((new_val - old_val) / old_val) * 100
            if pct_change >= 50:  # Рост на 50% или более
                increasing.append((merchant, old_val, new_val))
            elif pct_change <= -30:  # Падение на 30% или более
                decreasing.append((merchant, old_val, new_val))
            else:
                stable.append((merchant, old_val, new_val))
    
    # Обрабатываем специальные аккаунты
    print("\n" + "="*80)
    print("СПЕЦИАЛЬНЫЕ АККАУНТЫ".center(80))
    print("="*80)
    
    special_increasing = []
    special_decreasing = []
    special_stable = []
    
    if special_merchant_data:
        for merchant_name, data in special_merchant_data.items():
            old_val = data['date1']
            new_val = data['date2']
            merchant_id = data['id']
            
            # Формируем отображаемое имя с ID если ID есть
            display_name = f"{merchant_id} {merchant_name}" if merchant_id else merchant_name
            
            # Пропускаем нулевые значения
            if old_val == 0 and new_val == 0:
                print(f"{display_name} — ⚪️ 0 → 0")
                continue
            
            # Рассчитываем процентное изменение
            if old_val == 0 and new_val > 0:  # Новый поток
                pct = float('inf')
                special_increasing.append((display_name, old_val, new_val, pct))
                emoji = "🟢"
                print(f"{display_name} — {emoji} НОВЫЙ ПОТОК ({old_val}→{new_val})")
            elif new_val == 0:  # Закрытый поток
                special_decreasing.append((display_name, old_val, new_val, -100.0))
                emoji = "🔴"
                print(f"{display_name} — {emoji} ЗАКРЫТ -100.00% ({old_val}→0)")
            elif old_val > 0:
                pct_change = ((new_val - old_val) / old_val) * 100
                emoji = "🟢" if pct_change >= 0 else "🔴"
                sign = "+" if pct_change >= 0 else ""
                
                # Добавляем в соответствующую категорию только если соответствует условиям
                if pct_change >= 50:  # Рост на 50% или более
                    special_increasing.append((display_name, old_val, new_val, pct_change))
                    print(f"{display_name} — {emoji} {sign}{pct_change:.2f}% ({old_val}→{new_val})")
                elif pct_change <= -30:  # Падение на 30% или более
                    special_decreasing.append((display_name, old_val, new_val, pct_change))
                    print(f"{display_name} — {emoji} {sign}{pct_change:.2f}% ({old_val}→{new_val})")
                else:
                    special_stable.append((display_name, old_val, new_val, pct_change))
                    print(f"{display_name} — ⚪️ {sign}{pct_change:.2f}% (без отчета) ({old_val}→{new_val})")
    else:
        print("Нет данных для специальных аккаунтов")
    
    # Сортируем по абсолютному изменению (по убыванию)
    increasing.sort(key=lambda x: (x[2] - x[1]), reverse=True)
    decreasing.sort(key=lambda x: (x[1] - x[2]), reverse=True)
    
    # Выводим отчет
    print("\n" + "="*80)
    print("ОТЧЕТ ПО ИЗМЕНЕНИЯМ".center(80))
    print("="*80)
    
    # Увеличение трафика
    all_increasing = increasing + [(m, o, n) for m, o, n, p in special_increasing]
    all_increasing.sort(key=lambda x: (x[2] - x[1]), reverse=True)
    
    if all_increasing:
        print("\n📈 УВЕЛИЧЕНИЕ ТРАФИКА (≥50%):")
        print("-"*80)
        for merchant, old_val, new_val in all_increasing:
            if old_val == 0:
                print(f"{merchant} — НОВЫЙ ({old_val}→{new_val})")
            else:
                pct = ((new_val - old_val) / old_val) * 100
                print(f"{merchant} — ▲ {pct:+.1f}% ({old_val}→{new_val})")
    else:
        print("\n📈 УВЕЛИЧЕНИЕ ТРАФИКА: нет данных")
    
    # Сокращение трафика
    all_decreasing = decreasing + [(m, o, n) for m, o, n, p in special_decreasing]
    all_decreasing.sort(key=lambda x: (x[1] - x[2]), reverse=True)
    
    if all_decreasing:
        print("\n📉 СОКРАЩЕНИЕ ТРАФИКА (≤-30%):")
        print("-"*80)
        for merchant, old_val, new_val in all_decreasing:
            if new_val == 0:
                print(f"{merchant} — на 100% ({old_val}→0)")
            else:
                pct = ((old_val - new_val) / old_val) * 100
                print(f"{merchant} — ▼ {pct:.1f}% ({old_val}→{new_val})")
    else:
        print("\n📉 СОКРАЩЕНИЕ ТРАФИКА: нет данных")
    
    # Итоговая статистика
    #print("\n" + "="*80)
    #total_increase = sum(new - old for _, old, new in increasing) if increasing else 0
    #total_decrease = sum(old - new for _, old, new in decreasing) if decreasing else 0
    #print(f"ИТОГО: ▲ {total_increase:+,.0f} / ▼ {total_decrease:+,.0f} (ЧИСТЫЙ ПРИРОСТ: {total_increase - total_decrease:+,.0f})")
    #print("="*80)
    
    # Убираем секцию 'Без изменений'

if __name__ == "__main__":
    # Запускаем с текущей директорией
    main(os.getcwd())
    input("\nЖамкай Enter что бы выйти...")