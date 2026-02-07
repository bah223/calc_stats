import pandas as pd
import glob
from pathlib import Path
from datetime import datetime, timezone, timedelta

# === Moscow Timezone Setup ===
MOSCOW_TZ = timezone(timedelta(hours=3))

# === Collect matching Excel files ===
files = glob.glob("Transaction-List-Date_*.xlsx")

if not files:
    print("❌ No files found matching Transaction-List-Date_*.xlsx")
    exit(1)

print(f"📁 Files found: {len(files)}")
for f in files:
    print(f" - {f}")

DEBUG = False  # Set to True for detailed logging

total_count = 0
merchant_counts = {}
selected_time_column = None  # Will be filled after user choice


def get_merchant_column_index(df):
    """Searches for the merchant name column index in the header (first row)."""
    try:
        first_row = df.iloc[0]
        for idx, cell in enumerate(first_row):
            cell_str = str(cell).strip().lower()
            if 'merchant' in cell_str or 'name' in cell_str:
                return idx
    except Exception:
        pass
    return -1


def get_all_time_columns(df):
    """Searches for ALL columns with time data."""
    time_columns = []
    try:
        first_row = df.iloc[0]
        for idx, cell in enumerate(first_row):
            cell_str = str(cell).strip().lower()
            if any(keyword in cell_str for keyword in ['created', 'date', 'time', 'timestamp', 'updated', 'completion']):
                time_columns.append((idx, str(df.iloc[0, idx]).strip()))
    except Exception:
        pass
    return time_columns


def extract_merchant_from_row(df, row_idx, merchant_col_idx):
    """Extracts merchant name from a row by column index."""
    try:
        if merchant_col_idx >= 0 and merchant_col_idx < df.shape[1]:
            merchant = str(df.iat[row_idx, merchant_col_idx]).strip()
            if merchant and merchant.lower() not in ['nan', '']:
                return merchant
    except Exception:
        pass
    return None


# === Determine column for counting before processing ===
print("\n" + "="*60)
first_file = files[0]
try:
    sample_df = pd.read_excel(first_file, header=None)
    first_cell = str(sample_df.iloc[0, 0]).strip()
    if first_cell.lower() == "transactions":
        sample_df = sample_df.iloc[1:].reset_index(drop=True)
    
    time_cols = get_all_time_columns(sample_df)
    
    if time_cols:
        print("🕐 Time columns found:")
        for i, (col_idx, col_name) in enumerate(time_cols, 1):
            print(f"   {i}. [{col_idx}] {col_name}")
        
        print("\nChoose which column to use for counting transactions before 12:00:")
        choice = input("Enter number (1-{}): ".format(len(time_cols)))
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(time_cols):
                selected_time_column = time_cols[choice_idx][0]
                selected_time_name = time_cols[choice_idx][1]
                print(f"✅ Selected column: [{selected_time_column}] {selected_time_name}\n")
            else:
                print(f"❌ Invalid choice. Using default column 2")
                selected_time_column = 2
        except ValueError:
            print(f"❌ Invalid input. Using default column 2")
            selected_time_column = 2
    else:
        print("⚠️ Time columns not found automatically. Using column 2")
        selected_time_column = 2
except Exception as e:
    print(f"⚠️ Error determining columns: {e}. Using column 2")
    selected_time_column = 2

print("="*60 + "\n")

for file in files:
    try:
        df = pd.read_excel(file, header=None)

        if df.empty:
            continue

        # Skip "Transactions" row if present
        first_cell = str(df.iloc[0, 0]).strip()
        if first_cell.lower() == "transactions":
            df = df.iloc[1:].reset_index(drop=True)

        # Check for data
        if len(df) < 2:
            print(f"⚠️ Skipped {file}: insufficient data")
            continue

        # Find column indices
        merchant_col_idx = get_merchant_column_index(df)
        created_col_idx = selected_time_column

        if DEBUG:
            print(f"\n🔍 DEBUG: {Path(file).name}")
            print(f"   Total columns: {df.shape[1]}")
            print(f"   Rows: {len(df)}")
            print(f"   Merchant index: {merchant_col_idx}")
            print(f"   Time index: {created_col_idx}")
        
        # Count transactions before 12:00 Moscow time
        merchants_in_file = {}
        count_before_12 = 0
        count_total = 0
        count_invalid_time = 0
        
        for row_idx in range(1, len(df)):
            count_total += 1
            
            try:
                ts_str = str(df.iat[row_idx, created_col_idx]).strip()
            except Exception:
                ts_str = ''
            
            if not ts_str or ts_str.lower() == "nan":
                count_invalid_time += 1
                continue
            
            try:
                # Try different time formats
                dt_utc = None
                try:
                    dt_utc = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except:
                    try:
                        dt_utc = pd.to_datetime(ts_str)
                    except:
                        count_invalid_time += 1
                        continue
                
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                
                dt_moscow = dt_utc.astimezone(MOSCOW_TZ)
                
                if dt_moscow.hour < 12:
                    count_before_12 += 1
                    merchant_name = extract_merchant_from_row(df, row_idx, merchant_col_idx)
                    if merchant_name:
                        merchants_in_file[merchant_name] = merchants_in_file.get(merchant_name, 0) + 1
            except Exception as e:
                count_invalid_time += 1
                continue

        # Accumulate results
        for merchant, count in merchants_in_file.items():
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + count
            total_count += count
        
        # Output result for file
        if merchants_in_file:
            merchants_list = ", ".join([f"{m}: {c}" for m, c in merchants_in_file.items()])
            print(f"✅ {Path(file).name}")
            print(f"   Total rows: {count_total} | Before 12:00: {count_before_12} | Time errors: {count_invalid_time}")
            print(f"   Merchants: {merchants_list}")
        else:
            print(f"⚠️ {Path(file).name}")
            print(f"   Total rows: {count_total} | Before 12:00: {count_before_12} | Time errors: {count_invalid_time}")

    except Exception as e:
        print(f"❌ Error processing {file}: {e}")

# === Result ===
print("\n" + "="*50)
print(f"📊 Total transactions before 12:00 Moscow time: {total_count}")
print("\nList of merchants and their transactions before 12:00:")
for m, c in sorted(merchant_counts.items(), key=lambda x: x[1], reverse=True):
    print(f" - {m}: {c}")
print("="*50)
