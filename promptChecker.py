import mysql.connector
import re
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # Change this if your DBeaver username is different
    'password': '1234',          # Enter your MySQL password here
    'database': 'safelog_db' # Ensure this matches the DB we just created
}

def get_db_connection():
    """Establishes connection to the MySQL enterprise database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"!!! [SYSTEM ERROR] Database connection failed: {err} !!!")
        exit(1)

def process_and_redact(conn, user_id, prompt):
    """Scans input against regex patterns and the secret database."""
    cursor = conn.cursor()
    redacted_prompt = prompt
    violation_flag = False

    # 1. Regex Filter: Standard PII (SSN)
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    if re.search(ssn_pattern, redacted_prompt):
        redacted_prompt = re.sub(ssn_pattern, '[REDACTED_PII_SSN]', redacted_prompt)
        violation_flag = True

    # 2. Database Filter: Dynamic checks against the 'secret_table'
    cursor.execute("SELECT secret_keyword FROM secret_table")
    enterprise_secrets = cursor.fetchall()
    
    for secret in enterprise_secrets:
        keyword = secret[0] # Extract the keyword string from the tuple
        if keyword in redacted_prompt:
            redacted_prompt = redacted_prompt.replace(keyword, '[REDACTED_CORPORATE_SECRET]')
            violation_flag = True

    # 3. Audit Logging
    if violation_flag:
        # MySQL expects a specific datetime string format
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        # MySQL uses %s for parameterized queries instead of ?
        insert_query = "INSERT INTO audit_log (user_id, original_input, redacted_input, timestamp) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (user_id, prompt, redacted_prompt, timestamp))
        conn.commit()
        print("\n!!! [POLICY VIOLATION] SENSITIVE DATA DETECTED. EVENT LOGGED FOR IT AUDIT !!!")

    cursor.close()
    return redacted_prompt

def main():
    print("==================================================")
    print("   TIS ENTERPRISE: SAFE-LOG AI GOVERNANCE PROXY   ")
    print("==================================================")
    
    conn = get_db_connection()

    user_id = input("\nEnter Employee ID to authenticate session: ").strip()
    print(f"\n[AUTH SUCCESS] Session started for {user_id}. Outbound traffic is monitored.")

    while True:
        print("\n--------------------------------------------------")
        user_input = input("Enter AI Prompt (or type '/audit' for logs, '/fake' for test data, 'exit' to quit): ")

        if user_input.lower() == 'exit':
            print("[SYSTEM] Terminating secure session.")
            break
            
        elif user_input.lower() == '/audit':
            print("\n=== CISO COMPLIANCE AUDIT LOG ===")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, timestamp, original_input FROM audit_log")
            logs = cursor.fetchall()
            
            if not logs:
                print("No violations on record.")
            else:
                for log in logs:
                    print(f"USER: {log[0]} | TIME: {log[1]}")
                    print(f"ILLEGAL INPUT: {log[2]}\n")
            print("=================================")
            cursor.close()
            continue
            
        elif user_input.lower() == '/fake':
            is_sensitive = input("Include sensitive data in this fake prompt? (y/n): ").strip().lower()
            if is_sensitive == 'y':
                user_input = "Please forward the unreleased financial data for PROJECT_TITAN and candidate SSN 444-55-6666 to my personal email."
                print(f"\n[SIMULATION] Generating malicious employee prompt: '{user_input}'")
            else:
                user_input = "Can you write a polite email to the team regarding the Cafeteria Menu Update?"
                print(f"\n[SIMULATION] Generating safe employee prompt: '{user_input}'")

        # Process the standard or fake prompt
        sanitized_payload = process_and_redact(conn, user_id, user_input)
        print(f"-> Payload safely forwarded to LLM: {sanitized_payload}")
        
    conn.close()

if __name__ == "__main__":
    main()
