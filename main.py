import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# ==============================
# DATABASE SETUP
# ==============================

conn = sqlite3.connect("tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    type TEXT,
    description TEXT
)
""")

conn.commit()

# Create exports folder
if not os.path.exists("exports"):
    os.makedirs("exports")


# ==============================
# ADD TRANSACTION
# ==============================

def add_transaction():

    date = input("Enter Date (YYYY-MM-DD): ")
    category = input("Enter Category: ")
    amount = float(input("Enter Amount: "))
    t_type = input("Enter Type (Income/Expense): ")
    description = input("Enter Description: ")

    try:
        datetime.strptime(date, "%Y-%m-%d")

        cursor.execute("""
        INSERT INTO transactions
        (date, category, amount, type, description)
        VALUES (?, ?, ?, ?, ?)
        """, (date, category, amount, t_type, description))

        conn.commit()

        print("\nTransaction Added Successfully!")

    except ValueError:
        print("\nInvalid Date Format!")


# ==============================
# VIEW ALL TRANSACTIONS
# ==============================

def view_transactions():

    cursor.execute("SELECT * FROM transactions")

    rows = cursor.fetchall()

    if not rows:
        print("\nNo Transactions Found!")
        return

    print("\n========== Transactions ==========")

    for row in rows:
        print(f"""
ID          : {row[0]}
Date        : {row[1]}
Category    : {row[2]}
Amount      : {row[3]}
Type        : {row[4]}
Description : {row[5]}
-----------------------------------
""")


# ==============================
# MONTHLY SUMMARY
# ==============================

def monthly_summary():

    month = input("Enter Month (YYYY-MM): ")

    cursor.execute("""
    SELECT type, SUM(amount)
    FROM transactions
    WHERE strftime('%Y-%m', date)=?
    GROUP BY type
    """, (month,))

    results = cursor.fetchall()

    income = 0
    expense = 0

    for row in results:

        if row[0].lower() == "income":
            income = row[1]

        elif row[0].lower() == "expense":
            expense = row[1]

    savings = income - expense

    print("\n========== Monthly Summary ==========")
    print(f"Month   : {month}")
    print(f"Income  : {income}")
    print(f"Expense : {expense}")
    print(f"Savings : {savings}")


# ==============================
# CATEGORY WISE SUMMARY
# ==============================

def category_summary():

    month = input("Enter Month (YYYY-MM): ")

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE type='Expense'
    AND strftime('%Y-%m', date)=?
    GROUP BY category
    """, (month,))

    results = cursor.fetchall()

    if not results:
        print("\nNo Expense Data Found!")
        return

    print("\n====== Category Wise Expenses ======")

    for row in results:
        print(f"{row[0]} : {row[1]}")


# ==============================
# EXPORT REPORT
# ==============================

def export_report():

    query = "SELECT * FROM transactions"

    df = pd.read_sql_query(query, conn)

    csv_path = "exports/report.csv"
    excel_path = "exports/report.xlsx"

    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)

    print("\nReport Exported Successfully!")
    print(f"CSV File   : {csv_path}")
    print(f"Excel File : {excel_path}")


# ==============================
# GENERATE CHART
# ==============================

def generate_chart():

    query = """
    SELECT category, SUM(amount) as total
    FROM transactions
    WHERE type='Expense'
    GROUP BY category
    """

    df = pd.read_sql_query(query, conn)

    if df.empty:
        print("\nNo Expense Data Found!")
        return

    plt.figure(figsize=(7, 7))

    plt.pie(
        df['total'],
        labels=df['category'],
        autopct='%1.1f%%'
    )

    plt.title("Expense Distribution")

    chart_path = "exports/expense_chart.png"

    plt.savefig(chart_path)

    print("\nChart Generated Successfully!")
    print(f"Chart File : {chart_path}")


# ==============================
# DELETE TRANSACTION
# ==============================

def delete_transaction():

    transaction_id = input("Enter Transaction ID to Delete: ")

    cursor.execute("""
    DELETE FROM transactions
    WHERE id=?
    """, (transaction_id,))

    conn.commit()

    if cursor.rowcount > 0:
        print("\nTransaction Deleted Successfully!")
    else:
        print("\nTransaction Not Found!")


# ==============================
# MAIN MENU
# ==============================

while True:

    print("""
====================================
        EXPENSE TRACKER CLI
====================================

1. Add Transaction
2. View Transactions
3. Monthly Summary
4. Category Wise Summary
5. Export Report
6. Generate Expense Chart
7. Delete Transaction
8. Exit
""")

    choice = input("Enter Your Choice: ")

    if choice == "1":
        add_transaction()

    elif choice == "2":
        view_transactions()

    elif choice == "3":
        monthly_summary()

    elif choice == "4":
        category_summary()

    elif choice == "5":
        export_report()

    elif choice == "6":
        generate_chart()

    elif choice == "7":
        delete_transaction()

    elif choice == "8":
        print("\nExiting Expense Tracker...")
        break

    else:
        print("\nInvalid Choice! Please Try Again.")

# Close database connection
conn.close()      