# Name: Divyanshi Singh
# Enrollment number: 0157CY221052

import mysql.connector
import random
import re
from datetime import datetime


def create_connection():
    return mysql.connector.connect(
        host="localhost",      
        user="root",          
        password="mysqldiv6114@",  
        database="banking_system"
    )

def create_account_number():
    account_number = ""
    for _ in range(10):
        account_number += str(random.randint(0, 9))
    return account_number

def validating_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validating_contact(contact_number):
    return len(contact_number) == 10 and contact_number.isdigit()

def validating_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True

def validating_dob(dob):

    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except ValueError:
      
        return False

def add_user():
    connection = create_connection()
    cursor = connection.cursor()
    
    name = input("Enter name: ")

    dob = input("Enter date of birth (YYYY-MM-DD): ")
    if not validating_dob(dob):
        print("Error: Date of birth must be in the format YYYY-MM-DD.")
        return
    
    city = input("Enter city: ")

    contact_number = input("Enter contact number: ")
    if not validating_contact(contact_number):
        print("Invalid contact number. It should be 10 digits.")
        return
    
    email = input("Enter email: ")
    if not validating_email(email):
        print("Invalid email address.")
        return
    
    address = input("Enter address: ")
    password = input("Enter password: ")
    if not validating_password(password):
        print("Password must be at least 8 characters, including letters and numbers.")
        return
    
    account_number = create_account_number()
    initial_balance = float(input("Enter initial balance (minimum 2000): "))
    if initial_balance < 2000:
        print("Initial balance must be at least 2000.")
        return
    
    cursor.execute("INSERT INTO users (name, account_number, dob, city, contact_number, email, address, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (name, account_number, dob, city, contact_number, email, address, initial_balance))
    
    cursor.execute("SELECT LAST_INSERT_ID()")
    user_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO login (user_id, password) VALUES (%s, %s)", (user_id, password))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print(f"User added successfully! Account Number: {account_number}")

def show_user_details():
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"User ID: {user[0]}")
            print(f"Name: {user[1]}")
            print(f"Account Number: {user[2]}")
            print(f"DOB: {user[3]}")
            print(f"City: {user[4]}")
            print(f"Contact Number: {user[5]}")
            print(f"Email: {user[6]}")
            print(f"Address: {user[7]}")
            print(f"Balance: {user[8]}")
            print("-" * 30)
    
    cursor.close()
    connection.close()

    input("Press ENTER to return to the main menu +_+")
    main_menu()


def login():
    connection = create_connection()
    cursor = connection.cursor()
    
    account_number = input("Enter your account number: ")
    password = input("Enter your password: ")
    
    cursor.execute("SELECT u.user_id, l.password FROM users u JOIN login l ON u.user_id = l.user_id WHERE u.account_number = %s", (account_number,))
    result = cursor.fetchone()
    
    if result and result[1] == password:
        print("Login successful!")
        user_id = result[0]
        cursor.close()
        connection.close()
        login_menu(user_id)
    else:
        print("Sorry , Invalid account number or password.")
        cursor.close()
        connection.close()
        return None

def show_balance(user_id):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()[0]
    print(f"Your current account balance is: {balance}")
    
    cursor.close()
    connection.close()

def credit_amount(user_id, amount):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
    cursor.execute("INSERT INTO transaction (user_id, type, amount) VALUES (%s, 'Credit', %s)", (user_id, amount))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print(f"Amount of {amount} credited to your account.")

def debit_amount(user_id, amount):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()[0]
    
    if balance >= amount:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, user_id))
        cursor.execute("INSERT INTO transaction (user_id, type, amount) VALUES (%s, 'Debit', %s)", (user_id, amount))
        connection.commit()
        print(f"Amount of {amount} debited from your account.")
    else:
        print("Insufficient balance!")
    
    cursor.close()
    connection.close()

def transfer_amount(user_id, receiver_account_number, amount):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    balance = cursor.fetchone()[0]
    
    if balance >= amount:
        cursor.execute("SELECT user_id FROM users WHERE account_number = %s", (receiver_account_number,))
        receiver_user = cursor.fetchone()
        
        if receiver_user:
            receiver_user_id = receiver_user[0]
            
            cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, user_id))
            cursor.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, receiver_user_id))
            cursor.execute("INSERT INTO transaction (user_id, type, amount) VALUES (%s, 'Transfer Out', %s)", (user_id, amount))
            cursor.execute("INSERT INTO transaction (user_id, type, amount) VALUES (%s, 'Transfer In', %s)", (receiver_user_id, amount))
            
            connection.commit()
            print(f"Amount of {amount} transferred to account number {receiver_account_number}.")
        else:
            print("Receiver account not found.")
    else:
        print("Insufficient balance!")
    
    cursor.close()
    connection.close()

def change_password(user_id, new_password):
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("UPDATE login SET password = %s WHERE user_id = %s", (new_password, user_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("WELL DONE , Your Password changed successfully.")

def update_profile(user_id, name=None, city=None, contact_number=None, email=None, address=None):
    connection = create_connection()
    cursor = connection.cursor()
    
    if name:
        cursor.execute("UPDATE users SET name = %s WHERE user_id = %s", (name, user_id))
    if city:
        cursor.execute("UPDATE users SET city = %s WHERE user_id = %s", (city, user_id))
    if contact_number:
        cursor.execute("UPDATE users SET contact_number = %s WHERE user_id = %s", (contact_number, user_id))
    if email:
        cursor.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))
    if address:
        cursor.execute("UPDATE users SET address = %s WHERE user_id = %s", (address, user_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("Profile updated successfully.")

def toggle_account_status(user_id, status):

    if status not in ['Active', 'Deactive']:
        print("Invalid status! Please enter 'Active' or 'Deactive'.")
        return

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE users SET status = %s WHERE user_id = %s", (status, user_id))
        connection.commit()
        print(f"Account status updated to {status}.")
    except mysql.connector.Error as e:
        print(f"Error updating account status: {e}")
    finally:
        cursor.close()
        connection.close()

def main_menu():
    while True: 
        print("WELCOME TO THE CODING BANKING SYSTEM")
        print("1. *Add User*")
        print("2. *Show User*")
        print("3. *Login*")
        print("4. *Exit*")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            add_user()
        elif choice == '2':
            show_user_details()
        elif choice == '3':
            user_id = login()
            if user_id:
                login_menu(user_id)
        elif choice == '4':
            print("Exiting...")
            exit()
        else:
            print("Invalid choice, try again.")

def login_menu(user_id):
    while True:
        print("\n#Login Menu:")
        print("1. >>>Show Balance<<<")
        print("2. >>>Credit Amount<<<")
        print("3. >>>Debit Amount<<<")
        print("4. >>>Transfer Amount<<<")
        print("5. >>>Change Password<<<")
        print("6. >>>Update Profile<<<")
        print("7. >>>Toggle Account Status<<<")
        print("8. >>>Logout<<<")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            show_balance(user_id)
        elif choice == '2':
            amount = float(input("Enter amount to credit: "))
            credit_amount(user_id, amount)
        elif choice == '3':
            amount = float(input("Enter amount to debit: "))
            debit_amount(user_id, amount)
        elif choice == '4':
            receiver_account = input("Enter receiver account number: ")
            amount = float(input("Enter amount to transfer: "))
            transfer_amount(user_id, receiver_account, amount)
        elif choice == '5':
            new_password = input("Enter new password: ")
            change_password(user_id, new_password)
        elif choice == '6':
            update_profile_menu(user_id)
        elif choice == '7':
            status = input("Enter status (Active/Deactive): ")
            toggle_account_status(user_id, status)
        elif choice == '8':
            print("Logging out...")
            main_menu() 
            break
        else:
            print("Invalid choice, try again.")

def update_profile_menu(user_id):
    print("1. Update Name")
    print("2. Update City")
    print("3. Update Contact Number")
    print("4. Update Email")
    print("5. Update Address")
    
    choice = input("Enter your choice: ")

    if choice == '1':
        new_name = input("Enter new name: ")
        update_profile(user_id, name=new_name)
    elif choice == '2':
        new_city = input("Enter new city: ")
        update_profile(user_id, city=new_city)
    elif choice == '3':
        new_contact_number = input("Enter new contact number: ")
        update_profile(user_id, contact_number=new_contact_number)
    elif choice == '4':
        new_email = input("Enter new email: ")
        update_profile(user_id, email=new_email)
    elif choice == '5':
        new_address = input("Enter new address: ")
        update_profile(user_id, address=new_address)
    else:
        print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()

