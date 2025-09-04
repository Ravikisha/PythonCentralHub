import sqlite3
import datetime
import matplotlib.pyplot as plt
import json
import csv
import os
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from typing import Dict, List, Tuple, Optional
import re

class PersonalFinanceTracker:
    def __init__(self, db_path="finance_tracker.db"):
        """Initialize the Personal Finance Tracker with database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.init_database()
        
    def init_database(self):
        """Create necessary tables for the finance tracker."""
        cursor = self.conn.cursor()
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                color TEXT DEFAULT '#007bff',
                budget_limit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                date DATE NOT NULL,
                payment_method TEXT DEFAULT 'cash',
                location TEXT,
                tags TEXT,
                recurring BOOLEAN DEFAULT 0,
                recurring_frequency TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                period TEXT CHECK(period IN ('weekly', 'monthly', 'yearly')) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                alert_threshold REAL DEFAULT 0.8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                target_date DATE,
                description TEXT,
                priority INTEGER DEFAULT 1,
                achieved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT CHECK(type IN ('checking', 'savings', 'credit', 'investment')) NOT NULL,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                bank TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.populate_default_categories()
        
    def populate_default_categories(self):
        """Add default categories if none exist."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_categories = [
                ('Salary', 'income', '#28a745'),
                ('Freelance', 'income', '#17a2b8'),
                ('Investment', 'income', '#ffc107'),
                ('Food & Dining', 'expense', '#dc3545'),
                ('Transportation', 'expense', '#6f42c1'),
                ('Shopping', 'expense', '#fd7e14'),
                ('Entertainment', 'expense', '#e83e8c'),
                ('Bills & Utilities', 'expense', '#6c757d'),
                ('Healthcare', 'expense', '#20c997'),
                ('Education', 'expense', '#0d6efd')
            ]
            
            cursor.executemany(
                "INSERT INTO categories (name, type, color) VALUES (?, ?, ?)",
                default_categories
            )
            self.conn.commit()
    
    def add_transaction(self, amount: float, description: str, category_id: int, 
                       date: str = None, payment_method: str = 'cash', 
                       location: str = '', tags: str = '') -> int:
        """Add a new transaction to the database."""
        if date is None:
            date = datetime.date.today().isoformat()
            
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (amount, description, category_id, date, 
                                    payment_method, location, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (amount, description, category_id, date, payment_method, location, tags))
        
        transaction_id = cursor.lastrowid
        self.conn.commit()
        
        # Update account balance if account tracking is enabled
        self.update_balance_after_transaction(amount, category_id)
        
        return transaction_id
    
    def update_balance_after_transaction(self, amount: float, category_id: int):
        """Update account balance based on transaction type."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT type FROM categories WHERE id = ?", (category_id,))
        category_type = cursor.fetchone()[0]
        
        # For simplicity, assume primary account
        cursor.execute("SELECT id FROM accounts LIMIT 1")
        account = cursor.fetchone()
        if account:
            if category_type == 'income':
                cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", 
                             (amount, account[0]))
            else:
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", 
                             (amount, account[0]))
            self.conn.commit()
    
    def get_transactions(self, start_date: str = None, end_date: str = None, 
                        category_id: int = None, limit: int = None) -> List[Tuple]:
        """Retrieve transactions with optional filtering."""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT t.id, t.amount, t.description, c.name, c.type, t.date, 
                   t.payment_method, t.location, t.tags
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
        '''
        params = []
        conditions = []
        
        if start_date:
            conditions.append("t.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("t.date <= ?")
            params.append(end_date)
        if category_id:
            conditions.append("t.category_id = ?")
            params.append(category_id)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY t.date DESC, t.created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_balance_summary(self) -> Dict[str, float]:
        """Get overall financial summary."""
        cursor = self.conn.cursor()
        
        # Total income
        cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.type = 'income'
        ''')
        total_income = cursor.fetchone()[0]
        
        # Total expenses
        cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.type = 'expense'
        ''')
        total_expenses = cursor.fetchone()[0]
        
        # Net worth
        net_worth = total_income - total_expenses
        
        # This month's income and expenses
        current_month = datetime.date.today().replace(day=1).isoformat()
        
        cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.type = 'income' AND t.date >= ?
        ''', (current_month,))
        monthly_income = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.type = 'expense' AND t.date >= ?
        ''', (current_month,))
        monthly_expenses = cursor.fetchone()[0]
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_worth': net_worth,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'monthly_savings': monthly_income - monthly_expenses
        }
    
    def get_category_spending(self, period: str = 'monthly') -> List[Tuple]:
        """Get spending breakdown by category."""
        cursor = self.conn.cursor()
        
        if period == 'monthly':
            start_date = datetime.date.today().replace(day=1).isoformat()
        elif period == 'yearly':
            start_date = datetime.date.today().replace(month=1, day=1).isoformat()
        else:  # All time
            start_date = '1900-01-01'
            
        cursor.execute('''
            SELECT c.name, c.color, SUM(t.amount) as total, c.type
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date >= ?
            GROUP BY c.id, c.name, c.color, c.type
            ORDER BY total DESC
        ''', (start_date,))
        
        return cursor.fetchall()
    
    def create_budget(self, category_id: int, amount: float, period: str, 
                     start_date: str, end_date: str) -> int:
        """Create a new budget for a category."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO budgets (category_id, amount, period, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (category_id, amount, period, start_date, end_date))
        
        budget_id = cursor.lastrowid
        self.conn.commit()
        return budget_id
    
    def check_budget_status(self) -> List[Dict]:
        """Check budget status and alerts."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT b.id, b.amount, b.period, b.alert_threshold, c.name,
                   b.start_date, b.end_date
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.end_date >= date('now')
        ''')
        
        budgets = cursor.fetchall()
        budget_status = []
        
        for budget in budgets:
            budget_id, amount, period, threshold, category, start_date, end_date = budget
            
            # Calculate spent amount in budget period
            cursor.execute('''
                SELECT COALESCE(SUM(t.amount), 0)
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE c.name = ? AND t.date BETWEEN ? AND ?
            ''', (category, start_date, end_date))
            
            spent = cursor.fetchone()[0]
            percentage = (spent / amount) * 100 if amount > 0 else 0
            
            status = {
                'category': category,
                'budget': amount,
                'spent': spent,
                'remaining': amount - spent,
                'percentage': percentage,
                'alert': percentage >= (threshold * 100),
                'period': period
            }
            budget_status.append(status)
            
        return budget_status
    
    def add_goal(self, name: str, target_amount: float, target_date: str = None, 
                description: str = '', priority: int = 1) -> int:
        """Add a financial goal."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO goals (name, target_amount, target_date, description, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, target_amount, target_date, description, priority))
        
        goal_id = cursor.lastrowid
        self.conn.commit()
        return goal_id
    
    def update_goal_progress(self, goal_id: int, amount: float):
        """Update progress towards a goal."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE goals 
            SET current_amount = current_amount + ?
            WHERE id = ?
        ''', (amount, goal_id))
        
        # Check if goal is achieved
        cursor.execute('''
            UPDATE goals 
            SET achieved = 1 
            WHERE id = ? AND current_amount >= target_amount
        ''', (goal_id,))
        
        self.conn.commit()
    
    def get_goals(self) -> List[Tuple]:
        """Get all financial goals with progress."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, target_amount, current_amount, target_date, 
                   description, priority, achieved,
                   ROUND((current_amount / target_amount) * 100, 2) as progress
            FROM goals
            ORDER BY priority, target_date
        ''')
        return cursor.fetchall()
    
    def generate_monthly_report(self, year: int, month: int) -> Dict:
        """Generate comprehensive monthly financial report."""
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate last day of month
        if month == 12:
            next_month = datetime.date(year + 1, 1, 1)
        else:
            next_month = datetime.date(year, month + 1, 1)
        last_day = (next_month - datetime.timedelta(days=1)).day
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        cursor = self.conn.cursor()
        
        # Monthly totals
        cursor.execute('''
            SELECT c.type, SUM(t.amount)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date BETWEEN ? AND ?
            GROUP BY c.type
        ''', (start_date, end_date))
        
        totals = dict(cursor.fetchall())
        income = totals.get('income', 0)
        expenses = totals.get('expense', 0)
        
        # Category breakdown
        cursor.execute('''
            SELECT c.name, SUM(t.amount), c.type
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date BETWEEN ? AND ?
            GROUP BY c.id, c.name, c.type
            ORDER BY SUM(t.amount) DESC
        ''', (start_date, end_date))
        
        categories = cursor.fetchall()
        
        # Daily spending pattern
        cursor.execute('''
            SELECT t.date, SUM(CASE WHEN c.type = 'expense' THEN t.amount ELSE 0 END) as expenses,
                          SUM(CASE WHEN c.type = 'income' THEN t.amount ELSE 0 END) as income
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date BETWEEN ? AND ?
            GROUP BY t.date
            ORDER BY t.date
        ''', (start_date, end_date))
        
        daily_data = cursor.fetchall()
        
        return {
            'period': f"{year}-{month:02d}",
            'income': income,
            'expenses': expenses,
            'savings': income - expenses,
            'categories': categories,
            'daily_data': daily_data,
            'savings_rate': (income - expenses) / income * 100 if income > 0 else 0
        }
    
    def export_data(self, filename: str, format_type: str = 'csv'):
        """Export financial data to CSV or JSON."""
        transactions = self.get_transactions()
        
        if format_type.lower() == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Amount', 'Description', 'Category', 'Type', 
                               'Date', 'Payment Method', 'Location', 'Tags'])
                writer.writerows(transactions)
        
        elif format_type.lower() == 'json':
            data = []
            for transaction in transactions:
                data.append({
                    'id': transaction[0],
                    'amount': transaction[1],
                    'description': transaction[2],
                    'category': transaction[3],
                    'type': transaction[4],
                    'date': transaction[5],
                    'payment_method': transaction[6],
                    'location': transaction[7],
                    'tags': transaction[8]
                })
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    def import_data(self, filename: str):
        """Import financial data from CSV file."""
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Find or create category
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT id FROM categories WHERE name = ?", 
                                 (row['Category'],))
                    category = cursor.fetchone()
                    
                    if not category:
                        # Create new category
                        cursor.execute(
                            "INSERT INTO categories (name, type) VALUES (?, ?)",
                            (row['Category'], row.get('Type', 'expense'))
                        )
                        category_id = cursor.lastrowid
                    else:
                        category_id = category[0]
                    
                    # Add transaction
                    self.add_transaction(
                        amount=float(row['Amount']),
                        description=row['Description'],
                        category_id=category_id,
                        date=row['Date'],
                        payment_method=row.get('Payment Method', 'cash'),
                        location=row.get('Location', ''),
                        tags=row.get('Tags', '')
                    )
                    
        except Exception as e:
            print(f"Import error: {e}")
    
    def get_financial_insights(self) -> Dict:
        """Generate AI-like financial insights and recommendations."""
        summary = self.get_balance_summary()
        category_spending = self.get_category_spending('monthly')
        
        insights = {
            'spending_habits': [],
            'recommendations': [],
            'warnings': [],
            'achievements': []
        }
        
        # Analyze spending patterns
        if summary['monthly_expenses'] > summary['monthly_income']:
            insights['warnings'].append(
                "⚠️ You're spending more than you earn this month!"
            )
            insights['recommendations'].append(
                "💡 Review your expenses and identify areas to cut back"
            )
        
        # Savings rate analysis
        if summary['monthly_income'] > 0:
            savings_rate = (summary['monthly_savings'] / summary['monthly_income']) * 100
            if savings_rate >= 20:
                insights['achievements'].append(
                    f"🎉 Excellent! You're saving {savings_rate:.1f}% of your income"
                )
            elif savings_rate >= 10:
                insights['achievements'].append(
                    f"👍 Good job! You're saving {savings_rate:.1f}% of your income"
                )
            else:
                insights['recommendations'].append(
                    f"💰 Try to increase your savings rate (currently {savings_rate:.1f}%)"
                )
        
        # Top spending category
        if category_spending:
            top_expense = max(
                [cat for cat in category_spending if cat[3] == 'expense'],
                key=lambda x: x[2],
                default=None
            )
            if top_expense:
                insights['spending_habits'].append(
                    f"🛒 Your biggest expense category is {top_expense[0]} (${top_expense[2]:.2f})"
                )
        
        return insights
    
    def close(self):
        """Close database connection."""
        self.conn.close()

class FinanceTrackerGUI:
    def __init__(self):
        """Initialize the GUI application."""
        self.tracker = PersonalFinanceTracker()
        
        self.root = tk.Tk()
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.create_dashboard_tab()
        
        # Transactions tab
        self.create_transactions_tab()
        
        # Budget tab
        self.create_budget_tab()
        
        # Goals tab
        self.create_goals_tab()
        
        # Reports tab
        self.create_reports_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard overview tab."""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Summary cards frame
        summary_frame = ttk.Frame(dashboard_frame)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        # Financial summary labels
        self.income_label = ttk.Label(summary_frame, text="Monthly Income: $0.00", 
                                     font=('Arial', 12, 'bold'))
        self.income_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        self.expenses_label = ttk.Label(summary_frame, text="Monthly Expenses: $0.00",
                                       font=('Arial', 12, 'bold'))
        self.expenses_label.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        
        self.savings_label = ttk.Label(summary_frame, text="Monthly Savings: $0.00",
                                      font=('Arial', 12, 'bold'))
        self.savings_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        
        self.networth_label = ttk.Label(summary_frame, text="Net Worth: $0.00",
                                       font=('Arial', 12, 'bold'))
        self.networth_label.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        # Charts frame
        charts_frame = ttk.Frame(dashboard_frame)
        charts_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create matplotlib figure for charts
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Insights text area
        insights_frame = ttk.LabelFrame(dashboard_frame, text="Financial Insights")
        insights_frame.pack(fill='x', padx=10, pady=10)
        
        self.insights_text = tk.Text(insights_frame, height=6, wrap='word')
        insights_scrollbar = ttk.Scrollbar(insights_frame, orient='vertical', 
                                         command=self.insights_text.yview)
        self.insights_text.configure(yscrollcommand=insights_scrollbar.set)
        
        self.insights_text.pack(side='left', fill='both', expand=True)
        insights_scrollbar.pack(side='right', fill='y')
    
    def create_transactions_tab(self):
        """Create transactions management tab."""
        transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(transactions_frame, text="Transactions")
        
        # Add transaction form
        form_frame = ttk.LabelFrame(transactions_frame, text="Add Transaction")
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Form fields
        ttk.Label(form_frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = ttk.Entry(form_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.description_entry = ttk.Entry(form_frame, width=30)
        self.description_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.category_combo = ttk.Combobox(form_frame, width=20)
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Payment Method:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.payment_combo = ttk.Combobox(form_frame, 
                                         values=['cash', 'card', 'bank_transfer', 'online'],
                                         width=15)
        self.payment_combo.set('cash')
        self.payment_combo.grid(row=1, column=3, padx=5, pady=5)
        
        # Add button
        add_btn = ttk.Button(form_frame, text="Add Transaction", 
                           command=self.add_transaction)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Transactions list
        list_frame = ttk.LabelFrame(transactions_frame, text="Recent Transactions")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for transactions
        columns = ('Date', 'Amount', 'Description', 'Category', 'Payment Method')
        self.transactions_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=120)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient='vertical', 
                                     command=self.transactions_tree.yview)
        tree_scroll_x = ttk.Scrollbar(list_frame, orient='horizontal', 
                                     command=self.transactions_tree.xview)
        self.transactions_tree.configure(yscrollcommand=tree_scroll_y.set, 
                                       xscrollcommand=tree_scroll_x.set)
        
        self.transactions_tree.pack(side='left', fill='both', expand=True)
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x.pack(side='bottom', fill='x')
    
    def create_budget_tab(self):
        """Create budget management tab."""
        budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(budget_frame, text="Budgets")
        
        # Budget status display
        status_frame = ttk.LabelFrame(budget_frame, text="Budget Status")
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.budget_text = tk.Text(status_frame, height=15, wrap='word')
        budget_scroll = ttk.Scrollbar(status_frame, orient='vertical', 
                                    command=self.budget_text.yview)
        self.budget_text.configure(yscrollcommand=budget_scroll.set)
        
        self.budget_text.pack(side='left', fill='both', expand=True)
        budget_scroll.pack(side='right', fill='y')
    
    def create_goals_tab(self):
        """Create financial goals tab."""
        goals_frame = ttk.Frame(self.notebook)
        self.notebook.add(goals_frame, text="Goals")
        
        # Add goal form
        form_frame = ttk.LabelFrame(goals_frame, text="Add Financial Goal")
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Goal Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.goal_name_entry = ttk.Entry(form_frame, width=30)
        self.goal_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Target Amount:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.goal_amount_entry = ttk.Entry(form_frame, width=15)
        self.goal_amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        add_goal_btn = ttk.Button(form_frame, text="Add Goal", command=self.add_goal)
        add_goal_btn.grid(row=1, column=0, columnspan=4, pady=10)
        
        # Goals list
        list_frame = ttk.LabelFrame(goals_frame, text="Financial Goals")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.goals_text = tk.Text(list_frame, height=15, wrap='word')
        goals_scroll = ttk.Scrollbar(list_frame, orient='vertical', 
                                   command=self.goals_text.yview)
        self.goals_text.configure(yscrollcommand=goals_scroll.set)
        
        self.goals_text.pack(side='left', fill='both', expand=True)
        goals_scroll.pack(side='right', fill='y')
    
    def create_reports_tab(self):
        """Create reports and analytics tab."""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Export/Import frame
        io_frame = ttk.LabelFrame(reports_frame, text="Data Management")
        io_frame.pack(fill='x', padx=10, pady=10)
        
        export_btn = ttk.Button(io_frame, text="Export Data", command=self.export_data)
        export_btn.pack(side='left', padx=5, pady=5)
        
        import_btn = ttk.Button(io_frame, text="Import Data", command=self.import_data)
        import_btn.pack(side='left', padx=5, pady=5)
        
        # Monthly report
        report_frame = ttk.LabelFrame(reports_frame, text="Monthly Report")
        report_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.report_text = tk.Text(report_frame, height=20, wrap='word')
        report_scroll = ttk.Scrollbar(report_frame, orient='vertical', 
                                    command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scroll.set)
        
        self.report_text.pack(side='left', fill='both', expand=True)
        report_scroll.pack(side='right', fill='y')
    
    def add_transaction(self):
        """Add a new transaction from the form."""
        try:
            amount = float(self.amount_entry.get())
            description = self.description_entry.get()
            category_name = self.category_combo.get()
            payment_method = self.payment_combo.get()
            
            if not description or not category_name:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            # Get category ID
            cursor = self.tracker.conn.cursor()
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            category = cursor.fetchone()
            
            if not category:
                messagebox.showerror("Error", "Invalid category selected")
                return
            
            # Add transaction
            self.tracker.add_transaction(
                amount=amount,
                description=description,
                category_id=category[0],
                payment_method=payment_method
            )
            
            # Clear form
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            
            # Refresh data
            self.refresh_data()
            
            messagebox.showinfo("Success", "Transaction added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {e}")
    
    def add_goal(self):
        """Add a new financial goal."""
        try:
            name = self.goal_name_entry.get()
            amount = float(self.goal_amount_entry.get())
            
            if not name:
                messagebox.showerror("Error", "Please enter a goal name")
                return
            
            self.tracker.add_goal(name=name, target_amount=amount)
            
            # Clear form
            self.goal_name_entry.delete(0, tk.END)
            self.goal_amount_entry.delete(0, tk.END)
            
            # Refresh data
            self.refresh_data()
            
            messagebox.showinfo("Success", "Goal added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add goal: {e}")
    
    def export_data(self):
        """Export financial data to file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
        )
        
        if filename:
            file_extension = filename.split('.')[-1].lower()
            self.tracker.export_data(filename, file_extension)
            messagebox.showinfo("Success", f"Data exported to {filename}")
    
    def import_data(self):
        """Import financial data from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filename:
            try:
                self.tracker.import_data(filename)
                self.refresh_data()
                messagebox.showinfo("Success", "Data imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import data: {e}")
    
    def refresh_data(self):
        """Refresh all data displays."""
        self.update_dashboard()
        self.update_transactions_list()
        self.update_categories_combo()
        self.update_budget_status()
        self.update_goals_display()
        self.update_monthly_report()
    
    def update_dashboard(self):
        """Update dashboard with current financial summary."""
        summary = self.tracker.get_balance_summary()
        
        # Update summary labels
        self.income_label.config(text=f"Monthly Income: ${summary['monthly_income']:.2f}")
        self.expenses_label.config(text=f"Monthly Expenses: ${summary['monthly_expenses']:.2f}")
        self.savings_label.config(text=f"Monthly Savings: ${summary['monthly_savings']:.2f}")
        self.networth_label.config(text=f"Net Worth: ${summary['net_worth']:.2f}")
        
        # Update charts
        self.update_charts()
        
        # Update insights
        self.update_insights()
    
    def update_charts(self):
        """Update dashboard charts."""
        # Clear previous charts
        self.ax1.clear()
        self.ax2.clear()
        
        # Category spending pie chart
        category_data = self.tracker.get_category_spending('monthly')
        if category_data:
            expenses = [cat for cat in category_data if cat[3] == 'expense']
            if expenses:
                labels = [cat[0] for cat in expenses]
                amounts = [cat[2] for cat in expenses]
                colors = [cat[1] for cat in expenses]
                
                self.ax1.pie(amounts, labels=labels, colors=colors, autopct='%1.1f%%')
                self.ax1.set_title('Monthly Expenses by Category')
        
        # Monthly trend line chart (last 6 months)
        today = datetime.date.today()
        months_data = []
        
        for i in range(6):
            month_date = today.replace(day=1) - datetime.timedelta(days=i*30)
            report = self.tracker.generate_monthly_report(month_date.year, month_date.month)
            months_data.append((month_date.strftime('%b %Y'), report['expenses'], report['income']))
        
        months_data.reverse()
        
        if months_data:
            months = [data[0] for data in months_data]
            expenses = [data[1] for data in months_data]
            income = [data[2] for data in months_data]
            
            x = range(len(months))
            self.ax2.plot(x, expenses, label='Expenses', marker='o', color='red')
            self.ax2.plot(x, income, label='Income', marker='o', color='green')
            self.ax2.set_xticks(x)
            self.ax2.set_xticklabels(months, rotation=45)
            self.ax2.set_title('6-Month Income vs Expenses Trend')
            self.ax2.legend()
            self.ax2.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_insights(self):
        """Update financial insights display."""
        insights = self.tracker.get_financial_insights()
        
        self.insights_text.delete('1.0', tk.END)
        
        for category, messages in insights.items():
            if messages:
                self.insights_text.insert(tk.END, f"{category.replace('_', ' ').title()}:\n")
                for message in messages:
                    self.insights_text.insert(tk.END, f"  {message}\n")
                self.insights_text.insert(tk.END, "\n")
    
    def update_transactions_list(self):
        """Update transactions list display."""
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Get recent transactions
        transactions = self.tracker.get_transactions(limit=50)
        
        for transaction in transactions:
            self.transactions_tree.insert('', 'end', values=(
                transaction[5],  # date
                f"${transaction[1]:.2f}",  # amount
                transaction[2],  # description
                transaction[3],  # category
                transaction[6]   # payment method
            ))
    
    def update_categories_combo(self):
        """Update categories combobox."""
        cursor = self.tracker.conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        self.category_combo['values'] = categories
    
    def update_budget_status(self):
        """Update budget status display."""
        budget_status = self.tracker.check_budget_status()
        
        self.budget_text.delete('1.0', tk.END)
        
        if not budget_status:
            self.budget_text.insert(tk.END, "No active budgets found.\n")
            return
        
        self.budget_text.insert(tk.END, "📊 BUDGET STATUS OVERVIEW\n")
        self.budget_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for budget in budget_status:
            self.budget_text.insert(tk.END, f"Category: {budget['category']}\n")
            self.budget_text.insert(tk.END, f"Budget: ${budget['budget']:.2f}\n")
            self.budget_text.insert(tk.END, f"Spent: ${budget['spent']:.2f}\n")
            self.budget_text.insert(tk.END, f"Remaining: ${budget['remaining']:.2f}\n")
            self.budget_text.insert(tk.END, f"Progress: {budget['percentage']:.1f}%\n")
            
            if budget['alert']:
                self.budget_text.insert(tk.END, "⚠️ BUDGET ALERT: You're approaching your limit!\n")
            
            self.budget_text.insert(tk.END, "-" * 30 + "\n\n")
    
    def update_goals_display(self):
        """Update financial goals display."""
        goals = self.tracker.get_goals()
        
        self.goals_text.delete('1.0', tk.END)
        
        if not goals:
            self.goals_text.insert(tk.END, "No financial goals set.\n")
            return
        
        self.goals_text.insert(tk.END, "🎯 FINANCIAL GOALS\n")
        self.goals_text.insert(tk.END, "=" * 40 + "\n\n")
        
        for goal in goals:
            goal_id, name, target, current, target_date, description, priority, achieved, progress = goal
            
            self.goals_text.insert(tk.END, f"Goal: {name}\n")
            self.goals_text.insert(tk.END, f"Target: ${target:.2f}\n")
            self.goals_text.insert(tk.END, f"Current: ${current:.2f}\n")
            self.goals_text.insert(tk.END, f"Progress: {progress:.1f}%\n")
            
            if target_date:
                self.goals_text.insert(tk.END, f"Target Date: {target_date}\n")
            
            if achieved:
                self.goals_text.insert(tk.END, "✅ GOAL ACHIEVED!\n")
            
            if description:
                self.goals_text.insert(tk.END, f"Description: {description}\n")
            
            self.goals_text.insert(tk.END, "-" * 30 + "\n\n")
    
    def update_monthly_report(self):
        """Update monthly report display."""
        today = datetime.date.today()
        report = self.tracker.generate_monthly_report(today.year, today.month)
        
        self.report_text.delete('1.0', tk.END)
        
        self.report_text.insert(tk.END, f"📊 MONTHLY FINANCIAL REPORT - {report['period']}\n")
        self.report_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Summary
        self.report_text.insert(tk.END, "💰 FINANCIAL SUMMARY\n")
        self.report_text.insert(tk.END, f"Income: ${report['income']:.2f}\n")
        self.report_text.insert(tk.END, f"Expenses: ${report['expenses']:.2f}\n")
        self.report_text.insert(tk.END, f"Savings: ${report['savings']:.2f}\n")
        self.report_text.insert(tk.END, f"Savings Rate: {report['savings_rate']:.1f}%\n\n")
        
        # Category breakdown
        self.report_text.insert(tk.END, "📋 CATEGORY BREAKDOWN\n")
        for category, amount, cat_type in report['categories']:
            emoji = "💰" if cat_type == 'income' else "💸"
            self.report_text.insert(tk.END, f"{emoji} {category}: ${amount:.2f}\n")
        
        self.report_text.insert(tk.END, "\n")
    
    def run(self):
        """Start the GUI application."""
        try:
            self.root.mainloop()
        finally:
            self.tracker.close()

def main():
    """Main function to run the Personal Finance Tracker."""
    print("💰 Personal Finance Tracker")
    print("=" * 50)
    
    choice = input("\nChoose interface:\n1. Command Line\n2. GUI\nEnter choice (1-2): ")
    
    if choice == '2':
        # Run GUI version
        app = FinanceTrackerGUI()
        app.run()
    else:
        # Run command line version
        tracker = PersonalFinanceTracker()
        
        try:
            while True:
                print("\n📋 Menu:")
                print("1. Add Transaction")
                print("2. View Summary")
                print("3. View Transactions")
                print("4. Add Goal")
                print("5. View Goals")
                print("6. Generate Report")
                print("7. Export Data")
                print("8. View Budget Status")
                print("9. Financial Insights")
                print("10. Exit")
                
                choice = input("\nEnter your choice (1-10): ")
                
                if choice == '1':
                    # Add transaction
                    amount = float(input("Enter amount: $"))
                    description = input("Enter description: ")
                    
                    # Show categories
                    cursor = tracker.conn.cursor()
                    cursor.execute("SELECT id, name, type FROM categories ORDER BY type, name")
                    categories = cursor.fetchall()
                    
                    print("\nAvailable categories:")
                    for cat in categories:
                        print(f"{cat[0]}. {cat[1]} ({cat[2]})")
                    
                    cat_id = int(input("Enter category ID: "))
                    payment_method = input("Payment method (cash/card/bank_transfer/online): ") or 'cash'
                    
                    tracker.add_transaction(amount, description, cat_id, payment_method=payment_method)
                    print("✅ Transaction added successfully!")
                
                elif choice == '2':
                    # View summary
                    summary = tracker.get_balance_summary()
                    print(f"\n💰 Financial Summary:")
                    print(f"Total Income: ${summary['total_income']:.2f}")
                    print(f"Total Expenses: ${summary['total_expenses']:.2f}")
                    print(f"Net Worth: ${summary['net_worth']:.2f}")
                    print(f"Monthly Income: ${summary['monthly_income']:.2f}")
                    print(f"Monthly Expenses: ${summary['monthly_expenses']:.2f}")
                    print(f"Monthly Savings: ${summary['monthly_savings']:.2f}")
                
                elif choice == '3':
                    # View transactions
                    transactions = tracker.get_transactions(limit=10)
                    print(f"\n📊 Recent Transactions:")
                    print("-" * 80)
                    for t in transactions:
                        print(f"{t[5]} | ${t[1]:.2f} | {t[2][:30]} | {t[3]} | {t[6]}")
                
                elif choice == '4':
                    # Add goal
                    name = input("Goal name: ")
                    amount = float(input("Target amount: $"))
                    date = input("Target date (YYYY-MM-DD, optional): ") or None
                    description = input("Description (optional): ")
                    
                    tracker.add_goal(name, amount, date, description)
                    print("🎯 Goal added successfully!")
                
                elif choice == '5':
                    # View goals
                    goals = tracker.get_goals()
                    print(f"\n🎯 Financial Goals:")
                    print("-" * 60)
                    for goal in goals:
                        status = "✅ Achieved" if goal[7] else f"{goal[8]:.1f}% complete"
                        print(f"{goal[1]} | ${goal[3]:.2f}/${goal[2]:.2f} | {status}")
                
                elif choice == '6':
                    # Generate report
                    today = datetime.date.today()
                    report = tracker.generate_monthly_report(today.year, today.month)
                    
                    print(f"\n📊 Monthly Report - {report['period']}")
                    print("-" * 40)
                    print(f"Income: ${report['income']:.2f}")
                    print(f"Expenses: ${report['expenses']:.2f}")
                    print(f"Savings: ${report['savings']:.2f}")
                    print(f"Savings Rate: {report['savings_rate']:.1f}%")
                    
                    print(f"\nTop Categories:")
                    for cat, amount, cat_type in report['categories'][:5]:
                        print(f"  {cat}: ${amount:.2f}")
                
                elif choice == '7':
                    # Export data
                    filename = input("Enter filename (with .csv or .json extension): ")
                    file_format = filename.split('.')[-1].lower()
                    tracker.export_data(filename, file_format)
                    print(f"✅ Data exported to {filename}")
                
                elif choice == '8':
                    # Budget status
                    budgets = tracker.check_budget_status()
                    if budgets:
                        print(f"\n📊 Budget Status:")
                        print("-" * 50)
                        for budget in budgets:
                            alert = " ⚠️" if budget['alert'] else ""
                            print(f"{budget['category']}: ${budget['spent']:.2f}/${budget['budget']:.2f} ({budget['percentage']:.1f}%){alert}")
                    else:
                        print("No active budgets found.")
                
                elif choice == '9':
                    # Financial insights
                    insights = tracker.get_financial_insights()
                    print(f"\n🧠 Financial Insights:")
                    print("-" * 40)
                    
                    for category, messages in insights.items():
                        if messages:
                            print(f"\n{category.replace('_', ' ').title()}:")
                            for message in messages:
                                print(f"  {message}")
                
                elif choice == '10':
                    print("👋 Thank you for using Personal Finance Tracker!")
                    break
                
                else:
                    print("❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            tracker.close()

if __name__ == "__main__":
    main()
