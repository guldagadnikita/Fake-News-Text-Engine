"""
================================================================================
Module: database.py
================================================================================
Python & Database Concepts Demonstrated:
- Object-Oriented Programming (OOP): DatabaseManager class
- MySQL Database Integration: Connecting to MySQL, executing DDL and DML queries
- Exception Handling: try-except-finally blocks catching mysql.connector.Error
- Parameterized Queries: Using '%s' placeholders to prevent SQL Injection
- Transactions: conn.commit() to save changes and conn.rollback() on errors
- Data Structures: Dictionaries for configs, Tuples for SQL parameters, Lists for rows
================================================================================
"""

import mysql.connector
from mysql.connector import Error


class DatabaseManager:
    """
    Manages MySQL database connection, table schemas, and CRUD operations
    for the Fake News & Text Processing Engine.
    """

    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "root",
        database: str = "fake_news_db",
        port: int = 3306
    ):
        """
        Initializes connection parameters.
        Stores credentials in instance variables (OOP encapsulation).
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.is_connected = False

    def get_server_connection(self):
        """
        Connects directly to the MySQL Server without selecting a database.
        Useful for running CREATE DATABASE statements.
        """
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port
        )

    def get_db_connection(self):
        """
        Connects to the specific application database ('fake_news_db').
        """
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

    def test_connection(self) -> tuple:
        """
        Tests if MySQL server is reachable with the current credentials.
        Returns a tuple: (success_flag: bool, message: str)
        """
        conn = None
        try:
            conn = self.get_server_connection()
            if conn.is_connected():
                self.is_connected = True
                return (True, f"Connected successfully to MySQL on {self.host}:{self.port}!")
            return (False, "Connection established but server reported inactive.")
        except Error as err:
            self.is_connected = False
            return (False, f"MySQL Connection Failed: {str(err)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    def initialize_database(self) -> tuple:
        """
        Demonstrates: DDL (Data Definition Language)
        1. Creates database 'fake_news_db' if it does not exist.
        2. Creates table 'analysis_history' for saving text processing results.
        3. Creates table 'custom_keywords' for dynamic keyword management.
        
        Returns:
        - Tuple: (success: bool, status_message: str)
        """
        server_conn = None
        db_conn = None
        try:
            # Step 1: Connect to server and create database if missing
            server_conn = self.get_server_connection()
            server_cursor = server_conn.cursor()
            server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}`;")
            server_cursor.close()
            server_conn.close()
            server_conn = None

            # Step 2: Connect to the application database and create tables
            db_conn = self.get_db_connection()
            db_cursor = db_conn.cursor()

            # Schema: analysis_history table
            create_history_table = """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(255) NOT NULL,
                content_snippet VARCHAR(255) NOT NULL,
                full_text LONGTEXT NOT NULL,
                total_words INT NOT NULL,
                total_sentences INT NOT NULL,
                avg_word_length FLOAT NOT NULL,
                fake_news_score INT NOT NULL,
                verdict VARCHAR(50) NOT NULL,
                reasons_summary TEXT
            );
            """
            db_cursor.execute(create_history_table)

            # Schema: custom_keywords table
            create_keywords_table = """
            CREATE TABLE IF NOT EXISTS custom_keywords (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                keyword VARCHAR(100) NOT NULL UNIQUE
            );
            """
            db_cursor.execute(create_keywords_table)

            db_conn.commit()
            db_cursor.close()
            self.is_connected = True

            return (True, f"Database '{self.database}' and tables initialized successfully.")

        except Error as err:
            self.is_connected = False
            return (False, f"Database initialization failed: {str(err)}")
        finally:
            # Resource cleanup in finally block
            if server_conn and server_conn.is_connected():
                server_conn.close()
            if db_conn and db_conn.is_connected():
                db_conn.close()

    def save_analysis(
        self,
        title: str,
        full_text: str,
        total_words: int,
        total_sentences: int,
        avg_word_length: float,
        score: int,
        verdict: str,
        reasons_list: list
    ) -> tuple:
        """
        Demonstrates: DML (INSERT statement), Parameterized Queries, Transactions.
        Saves a completed analysis record into MySQL.
        
        Returns:
        - Tuple: (success: bool, message_or_inserted_id)
        """
        conn = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Clean and truncate snippet for preview
            snippet = full_text.strip().replace("\n", " ")[:120] + ("..." if len(full_text) > 120 else "")
            reasons_summary = " | ".join(reasons_list)

            # Safe parameterized SQL insert to prevent SQL injection
            insert_query = """
            INSERT INTO analysis_history (
                title, content_snippet, full_text,
                total_words, total_sentences, avg_word_length,
                fake_news_score, verdict, reasons_summary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            values = (
                title if title.strip() else "Untitled Article",
                snippet,
                full_text,
                total_words,
                total_sentences,
                avg_word_length,
                score,
                verdict,
                reasons_summary
            )

            cursor.execute(insert_query, values)
            conn.commit()  # Commit transaction
            inserted_id = cursor.lastrowid
            cursor.close()

            return (True, inserted_id)

        except Error as err:
            if conn:
                conn.rollback()  # Rollback on failure
            return (False, f"Failed to save record: {str(err)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_all_history(self, filter_verdict: str = "All") -> tuple:
        """
        Demonstrates: SELECT statement, WHERE filtering, ORDER BY.
        Retrieves saved analyses from the database for the Treeview dashboard.
        
        Returns:
        - Tuple: (success: bool, records_list_or_error)
        """
        conn = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)

            if filter_verdict and filter_verdict != "All":
                query = """
                SELECT id, created_at, title, total_words, fake_news_score, verdict
                FROM analysis_history
                WHERE verdict = %s
                ORDER BY id DESC;
                """
                cursor.execute(query, (filter_verdict,))
            else:
                query = """
                SELECT id, created_at, title, total_words, fake_news_score, verdict
                FROM analysis_history
                ORDER BY id DESC;
                """
                cursor.execute(query)

            records = cursor.fetchall()
            cursor.close()
            return (True, records)

        except Error as err:
            return (False, f"Failed to fetch history: {str(err)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_history_by_id(self, record_id: int) -> tuple:
        """
        Fetches the complete single record (including full text and stats) by its ID.
        Used to reload an article back into the text editor.
        """
        conn = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM analysis_history WHERE id = %s;"
            cursor.execute(query, (record_id,))
            record = cursor.fetchone()
            cursor.close()

            if record:
                return (True, record)
            else:
                return (False, f"No record found with ID {record_id}.")

        except Error as err:
            return (False, f"Failed to load record: {str(err)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    def delete_history_by_id(self, record_id: int) -> tuple:
        """
        Demonstrates: DELETE statement.
        Removes a specific record from the database.
        """
        conn = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            query = "DELETE FROM analysis_history WHERE id = %s;"
            cursor.execute(query, (record_id,))
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            if rows_affected > 0:
                return (True, f"Record #{record_id} deleted successfully.")
            else:
                return (False, f"Record #{record_id} does not exist.")

        except Error as err:
            if conn:
                conn.rollback()
            return (False, f"Failed to delete record: {str(err)}")
        finally:
            if conn and conn.is_connected():
                conn.close()

    def seed_keywords_into_db(self, categories_dict: dict) -> tuple:
        """
        Demonstrates: Batch insert using INSERT IGNORE to populate custom_keywords table.
        """
        conn = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            query = "INSERT IGNORE INTO custom_keywords (category, keyword) VALUES (%s, %s);"

            total_added = 0
            for category, words in categories_dict.items():
                for word in words:
                    cursor.execute(query, (category, word.lower()))
                    if cursor.rowcount > 0:
                        total_added += 1

            conn.commit()
            cursor.close()
            return (True, f"Seeded {total_added} keywords into MySQL database.")

        except Error as err:
            if conn:
                conn.rollback()
            return (False, f"Failed to seed keywords: {str(err)}")
        finally:
            if conn and conn.is_connected():
                conn.close()
