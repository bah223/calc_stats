import pandas as pd
import glob
import os
import warnings

# Suppress openpyxl style warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Find all files matching the pattern
files = glob.glob("Transaction-*.xlsx")

if not files:
    print("❌ No files matching 'Transaction-*.xlsx' found in the current directory.")
    exit()

# Initialize total report for all files
total_report = {
    'CAPTURED': {'count': 0, 'amount': 0.0},
    'CANCELLED': {'count': 0, 'amount': 0.0},
    'DECLINED': {'count': 0, 'amount': 0.0},
    'REFUNDED': {'count': 0, 'amount': 0.0},
    'ERROR': {'count': 0, 'amount': 0.0},
    'PAID_OUT': {'count': 0, 'amount': 0.0},
}

# Process each file
for file_path in sorted(files):
    print(f"\n📄 Processing file: {os.path.basename(file_path)}")
    print("-" * 60)

    try:
        # Read Excel without headers
        df = pd.read_excel(file_path, header=None, engine='openpyxl')

        # Expect at least 8 columns (status index 6, amount index 7)
        if df.shape[1] < 8:
            print("⚠️  File has fewer than 8 columns — skipping.")
            continue

        statuses = df.iloc[:, 6]  # Status
        amounts = df.iloc[:, 7]   # Amount

        # Counting
        for status, amount in zip(statuses, amounts):
            if pd.isna(status) or pd.isna(amount):
                continue
            status = str(status).strip().upper()
            if status in total_report:
                total_report[status]['count'] += 1
                try:
                    total_report[status]['amount'] += float(amount)
                except (ValueError, TypeError):
                    continue  # skip invalid amounts

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

# Format amount: 1,234,567.89
def fmt_rub(value):
    return f"{value:,.2f}"

# Output final report
print("\n" + "="*60)
print("📊 FINAL REPORT FOR ALL FILES")
print("="*60)
print(f"- Successful transactions (CAPTURED): {total_report['CAPTURED']['count']} pcs for {fmt_rub(total_report['CAPTURED']['amount'])} RUB")
print(f"- Unpaid transactions (CANCELLED): {total_report['CANCELLED']['count']} pcs for {fmt_rub(total_report['CANCELLED']['amount'])} RUB")
print(f"- Declined transactions (DECLINED): {total_report['DECLINED']['count']} pcs for {fmt_rub(total_report['DECLINED']['amount'])} RUB")
print(f"- Error transactions (ERROR): {total_report['ERROR']['count']} pcs for {fmt_rub(total_report['ERROR']['amount'])} RUB")
print(f"- Refunds (REFUNDED): {total_report['REFUNDED']['count']} pcs for {fmt_rub(total_report['REFUNDED']['amount'])} RUB")
print(f"- Payouts (PAID_OUT): {total_report['PAID_OUT']['count']} pcs for {fmt_rub(total_report['PAID_OUT']['amount'])} RUB")

print("\n✅ Processing complete.")
