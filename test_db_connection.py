#!/usr/bin/env python3
"""
Quick test for MySQL database connection
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test MySQL connection"""
    try:
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '8498')
        
        print(f"🔗 Testing connection to MySQL at {host} with user {user}...")
        
        # Test connection to MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Successfully connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"✅ Current database: {record}")
            
            # List databases
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print(f"✅ Available databases: {[db[0] for db in databases]}")
            
            cursor.close()
            connection.close()
            print("✅ MySQL connection test successful!")
            return True
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
