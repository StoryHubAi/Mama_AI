#!/usr/bin/env python3
"""
Database initialization script for MAMA-AI
Creates MySQL database and tables
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create MySQL database if it doesn't exist"""
    try:
        # Database connection parameters
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '8498')
        database = os.getenv('MYSQL_DATABASE', 'mama_ai')
        
        print(f"🔗 Connecting to MySQL server at {host}...")
        
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"✅ Database '{database}' created or already exists")
            
            # Use the database
            cursor.execute(f"USE {database}")
            print(f"✅ Using database '{database}'")
            
            cursor.close()
            connection.close()
            print("✅ Database setup complete!")
            return True
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def init_flask_db():
    """Initialize Flask database tables"""
    try:
        print("🔧 Initializing Flask database tables...")
        
        # Import Flask app and database
        from app import app, db
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ All database tables created successfully!")
            
            # Add sample data if needed
            add_sample_data(db)
            
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Flask database: {e}")
        return False

def add_sample_data(db):
    """Add sample data for testing (optional)"""
    try:
        from src.models import User, Pregnancy
        from datetime import datetime, date
        
        # Check if we already have users
        existing_user = User.query.first()
        if existing_user:
            print("✅ Sample data already exists")
            return
        
        # Create a sample user for testing
        sample_user = User(
            phone_number='+254700000000',
            name='Mary Test',
            preferred_language='sw',
            location='Nairobi',
            is_active=True
        )
        
        db.session.add(sample_user)
        db.session.commit()
        
        # Create sample pregnancy
        sample_pregnancy = Pregnancy(
            user_id=sample_user.id,
            due_date=date(2025, 12, 1),
            weeks_pregnant=20,
            is_high_risk=False,
            health_conditions='None',
            is_active=True
        )
        
        db.session.add(sample_pregnancy)
        db.session.commit()
        
        print("✅ Sample test data added")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not add sample data: {e}")

def main():
    """Main initialization function"""
    print("🚀 MAMA-AI Database Initialization")
    print("=" * 40)
    
    # Step 1: Create MySQL database
    if not create_database():
        print("❌ Failed to create database. Please check your MySQL configuration.")
        sys.exit(1)
    
    # Step 2: Initialize Flask tables
    if not init_flask_db():
        print("❌ Failed to initialize Flask database tables.")
        sys.exit(1)
    
    print("\n🎉 Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Run the Flask app: python app.py")
    print("2. Test SMS: Send a message to your shortcode")
    print("3. Test USSD: Dial *123#")
    print("\n🤱 MAMA-AI is ready to help mothers!")

if __name__ == "__main__":
    main()
