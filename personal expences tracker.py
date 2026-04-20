import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

class FinanceTracker:
    def __init__(self, filename: str = "finance_data.json"):
        self.filename = filename
        self.transactions: List[Dict] = []
        self.budgets: Dict[str, float] = {}
        self.load_data()
    
    def load_data(self):
        """Load all data from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', [])
                    self.budgets = data.get('budgets', {})
            except:
                self.transactions = []
                self.budgets = {}
        else:
            self.transactions = []
            self.budgets = {}
    
    def save_data(self):
        """Save all data to JSON file"""
        data = {
            'transactions': self.transactions,
            'budgets': self.budgets
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_transaction(self, type_: str, category: str, amount: float, description: str = ""):
        """Add income or expense transaction"""
        if type_ not in ['income', 'expense']:
            print("❌ Type must be 'income' or 'expense'")
            return
        
        transaction = {
            'id': len(self.transactions) + 1,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': type_,
            'category': category,
            'amount': abs(amount),
            'description': description
        }
        self.transactions.append(transaction)
        self.save_data()
        emoji = "💰" if type_ == 'income' else "💸"
        print(f"{emoji} Added {type_}: ${amount:.2f} - {category}")
    
    def set_budget(self, category: str, monthly_budget: float):
        """Set monthly budget for a category"""
        self.budgets[category] = monthly_budget
        self.save_data()
        print(f"✅ Set {category} budget: ${monthly_budget:.2f}/month")
    
    def get_monthly_summary(self, month: Optional[str] = None) -> Dict:
        """Get detailed monthly financial summary"""
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        income_total = 0
        expense_total = 0
        category_expenses = defaultdict(float)
        
        for trans in self.transactions:
            if trans['date'].startswith(month):
                if trans['type'] == 'income':
                    income_total += trans['amount']
                else:
                    expense_total += trans['amount']
                    category_expenses[trans['category']] += trans['amount']
        
        net_savings = income_total - expense_total
        savings_rate = (net_savings / income_total * 100) if income_total > 0 else 0
        
        return {
            'month': month,
            'income': income_total,
            'expenses': expense_total,
            'net_savings': net_savings,
            'savings_rate': savings_rate,
            'category_expenses': dict(category_expenses)
        }
    
    def display_monthly_summary(self, month: Optional[str] = None):
        """Display formatted monthly summary"""
        summary = self.get_monthly_summary(month)
        
        print(f"\n📊 MONTHLY SUMMARY - {summary['month']}")
        print("=" * 60)
        print(f"💰 Income:          ${summary['income']:>10.2f}")
        print(f"💸 Expenses:        ${summary['expenses']:>10.2f}")
        print(f"💵 Net Savings:     ${summary['net_savings']:>10.2f}")
        print(f"📈 Savings Rate:    {summary['savings_rate']:>6.1f}%")
        print()
        
        if summary['category_expenses']:
            print("📋 Expenses by Category:")
            print("-" * 40)
            for cat, amt in sorted(summary['category_expenses'].items(), 
                                 key=lambda x: x[1], reverse=True):
                budget_status = ""
                if cat in self.budgets:
                    budget = self.budgets[cat]
                    over_budget = amt - budget
                    if over_budget > 0:
                        budget_status = f"  ❌ Over by ${over_budget:.2f}"
                    else:
                        budget_status = f"  ✅ Under by ${-over_budget:.2f}"
                
                print(f"  {cat:<15}: ${amt:>8.2f}{budget_status}")
    
    def view_recent_transactions(self, days: int = 7):
        """View recent transactions"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [t for t in self.transactions 
                 if datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S') >= cutoff]
        
        if not recent:
            print(f"📭 No transactions in last {days} days")
            return
        
        print(f"\n📋 Recent Transactions (Last {days} days):")
        print("-" * 80)
        total_income = total_expense = 0
        
        for trans in reversed(recent):
            emoji = "💰" if trans['type'] == 'income' else "💸"
            sign = "+" if trans['type'] == 'income' else "-"
            print(f"{emoji} {trans['date'][:16]} | {sign}${trans['amount']:>7.2f} | "
                  f"{trans['category']:<15} | {trans['description'][:30]}")
            
            if trans['type'] == 'income':
                total_income += trans['amount']
            else:
                total_expense += trans['amount']
        
        print("-" * 80)
        print(f"💰 Total Income:  ${total_income:>8.2f} | 💸 Total Expense: ${total_expense:>8.2f}")
    
    def delete_transaction(self, trans_id: int):
        """Delete a transaction by ID"""
        for i, trans in enumerate(self.transactions):
            if trans['id'] == trans_id:
                removed = self.transactions.pop(i)
                self.save_data()
                emoji = "💰" if removed['type'] == 'income' else "💸"
                print(f"🗑️ Removed {removed['type']}: ${removed['amount']:.2f} - {removed['category']}")
                return
        print("❌ Transaction not found!")
    
    def generate_chart(self):
        """Generate spending pie chart"""
        if not self.transactions:
            print("📭 No data for chart!")
            return
        
        current_month = datetime.now().strftime('%Y-%m')
        summary = self.get_monthly_summary(current_month)
        
        if not summary['category_expenses']:
            print("📭 No expenses this month!")
            return
        
        plt.figure(figsize=(10, 6))
        colors = plt.cm.Set3(range(len(summary['category_expenses'])))
        
        wedges, texts, autotexts = plt.pie(
            summary['category_expenses'].values(),
            labels=summary['category_expenses'].keys(),
            autopct='%1.1f%%',
            colors=colors
        )
        
        plt.title(f"Expenses Breakdown - {current_month}", fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    
    def export_to_csv(self, filename: str = "finance_export.csv"):
        """Export transactions to CSV"""
        df = pd.DataFrame(self.transactions)
        if not df.empty:
            df.to_csv(filename, index=False)
            print(f"📤 Exported {len(df)} transactions to {filename}")
        else:
            print("📭 No data to export!")

def main_menu():
    tracker = FinanceTracker()
    
    predefined_categories = {
        'income': ['Salary', 'Freelance', 'Investment', 'Other'],
        'expense': ['Food', 'Transport', 'Rent', 'Utilities', 'Entertainment', 
                   'Shopping', 'Healthcare', 'Education', 'Other']
    }
    
    while True:
        print("\n" + "="*60)
        print("💰 PERSONAL FINANCE TRACKER")
        print("="*60)
        print("1.  💰 Add Income")
        print("2.  💸 Add Expense") 
        print("3.  📊 Monthly Summary")
        print("4.  📋 Recent Transactions")
        print("5.  💳 Set Budget")
        print("6.  📈 Budget Status")
        print("7.  🗑️ Delete Transaction")
        print("8.  📊 Pie Chart")
        print("9.  📤 Export CSV")
        print("10. 👋 Exit")
        
        choice = input("\nChoose option (1-10): ").strip()
        
        if choice == '1':
            print("\nIncome Categories:", ", ".join(predefined_categories['income']))
            cat = input("Category: ").strip() or 'Other'
            amt = float(input("Amount: $"))
            desc = input("Description (optional): ").strip()
            tracker.add_transaction('income', cat, amt, desc)
        
        elif choice == '2':
            print("\nExpense Categories:", ", ".join(predefined_categories['expense']))
            cat = input("Category: ").strip() or 'Other'
            amt = float(input("Amount: $"))
            desc = input("Description (optional): ").strip()
            tracker.add_transaction('expense', cat, -amt, desc)
        
        elif choice == '3':
            month = input("Month (YYYY-MM, Enter for current): ").strip() or None
            tracker.display_monthly_summary(month)
        
        elif choice == '4':
            days = int(input("Last X days (default 7): ") or 7)
            tracker.view_recent_transactions(days)
        
        elif choice == '5':
            cat = input("Category: ").strip()
            budget = float(input("Monthly budget: $"))
            tracker.set_budget(cat, budget)
        
        elif choice == '6':
            tracker.display_monthly_summary()
        
        elif choice == '7':
            tracker.view_recent_transactions(30)
            tid = int(input("Transaction ID to delete: "))
            tracker.delete_transaction(tid)
        
        elif choice == '8':
            tracker.generate_chart()
        
        elif choice == '9':
            tracker.export_to_csv()
        
        elif choice == '10':
            print("\n👋 Thank you for using Finance Tracker!")
            print("💾 All data saved automatically.")
            break
        
        else:
            print("❌ Invalid option!")

if __name__ == "__main__":
    # Install required packages: pip install matplotlib pandas
    main_menu()