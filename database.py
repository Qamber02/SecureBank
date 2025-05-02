import pymysql

def create_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='banking_app',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def create_tables():
    conn = create_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255),
                profile_img VARCHAR(255)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                type ENUM('Savings', 'Checking'),
                balance DECIMAL(15,2),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                account_id INT,
                type ENUM('Deposit', 'Withdrawal'),
                amount DECIMAL(15,2),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
    conn.commit()
    conn.close()