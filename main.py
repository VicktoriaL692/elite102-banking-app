import sqlite3
import re

DB_FILE = "bank.db"


class Database:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self):
        script = """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            balance REAL NOT NULL CHECK(balance >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.conn.executescript(script)
        self.conn.commit()


    def create_account(self, name: str, password: str, initial: float):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO accounts (name, password, balance) VALUES (?, ?, ?)",
                (name, password, initial),
            )
            self.conn.commit()
            return True, None
        except Exception as e:
            return False, str(e)

    def verify_login(self, name: str, password: str):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id FROM accounts WHERE name = ? AND password = ?",
            (name, password),
        )
        row = cur.fetchone()
        return row[0] if row else None

    def get_balance(self, user_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None

    def deposit(self, user_id: int, amount: float):
        cur = self.conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, user_id))
        self.conn.commit()

    def withdraw(self, user_id: int, amount: float):
        bal = self.get_balance(user_id)
        if bal is None:
            return False, "Account not found."
        if amount > bal:
            return False, "Try again! Overdraft."
        cur = self.conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, user_id))
        self.conn.commit()
        return True, None

    def list_accounts(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, balance FROM accounts ORDER BY id ASC;")
        return cur.fetchall()


def is_valid_name(name: str):
    return name.isalpha()

def is_valid_number(value: str):
    try:
        float(value)
        return True
    except ValueError:
        return False


def menu():
    print("\n--- BANKING WITH C2C ---")
    print("1. Create Account")
    print("2. Login")
    print("3. List Accounts")
    print("4. Exit")
    return input("Choose an option: ").strip()


def account_menu():
    print("\n--- ACCOUNT MENU ---")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Logout")
    return input("Choose an option: ").strip()


def main():
    db = Database()

    while True:
        choice = menu()

        if choice == "1":
            name = input("Enter your name (letters only): ").strip()
            if not is_valid_name(name):
                print(" Name must be letters.")
                continue

            password = input("Create a password: ").strip()
            initial = input("Initial deposit (numbers only!): ").strip()

            if not is_valid_number(initial):
                print("Try again! Deposit must be a number.")
                continue

            ok, err = db.create_account(name, password, float(initial))
            print("Your account has been created!" if ok else f"Error: {err}")

  
        elif choice == "2":
            name = input("Name: ").strip()
            password = input("Password: ").strip()

            user_id = db.verify_login(name, password)
            if not user_id:
                print("Invalid name or password.")
                continue

            print(f"Welcome, {name}!")




            while True:
                act = account_menu()

                # Balance
                if act == "1":
                    bal = db.get_balance(user_id)
                    print(f"Your balance is: ${bal:.2f}")

                # Deposit
                elif act == "2":
                    amt = input("Deposit amount: ").strip()
                    if not is_valid_number(amt):
                        print("Ty again! Must be a number.")
                        continue
                    db.deposit(user_id, float(amt))
                    print("Deposit successful!")

                # Withdraw
                elif act == "3":
                    amt = input("Withdraw amount: ").strip()
                    if not is_valid_number(amt):
                        print("Try again! Must be a number.")
                        continue
                    ok, err = db.withdraw(user_id, float(amt))
                    print("Withdrawal successful." if ok else f"Error: {err}")

                # Logout
                elif act == "4":
                    print("Logged out.")
                    break

                else:
                    print("Invalid choice.")




        elif choice == "3":
            print("\n--- Accounts ---")
            for row in db.list_accounts():
                print(f"ID: {row[0]} | {row[1]} | Balance: ${row[2]:.2f}")




        elif choice == "4":
            print("Goodbye.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()