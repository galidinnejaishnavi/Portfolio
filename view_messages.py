import os
import sqlite3

# Locate the database in the root folder
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'portfolio.db')

if not os.path.exists(db_path):
    print("No database found yet. Submit a message on the contact page first!")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT id, name, email, phone, subject, message, created_at FROM contact_messages ORDER BY created_at DESC;")
    messages = cursor.fetchall()
    
    if not messages:
        print("No messages found in the database.")
    else:
        print(f"\n========================================")
        print(f"   CONTACT FORM SUBMISSIONS ({len(messages)} total)")
        print(f"========================================\n")
        for msg in messages:
            print(f"ID:         {msg[0]}")
            print(f"Date/Time:  {msg[6]}")
            print(f"Name:       {msg[1]}")
            print(f"Email:      {msg[2]}")
            if msg[3]:
                print(f"Phone:      {msg[3]}")
            print(f"Subject:    {msg[4]}")
            print(f"Message:")
            print(f"  {msg[5]}")
            print("-" * 40)
except sqlite3.OperationalError:
    print("The contact_messages table does not exist yet. Please run the Flask app and submit a message first.")
finally:
    conn.close()
