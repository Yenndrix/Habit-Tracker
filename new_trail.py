# Import necessary libraries
import sqlite3
import pandas as pd # Imported to display tables
from datetime import datetime, date 
from typing import List
import hashlib # Imported to hash password



# Utility Functions
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# Database Connection, saves data to new_test.db
def get_db(name="db.db",  uri=False):
    db = sqlite3.connect(name)
    db.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key support
    return db


# Closes Database
def close_db(db):
    """Closes the database connection."""
    db.close()


  
# User Management
class User:
    """Initializes the User class."""
    def __init__(self, user_id: int, username: str, password: str, emailID: str):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.emailID = emailID

 
    # Add a new user
    @classmethod
    def add_user(cls, db, username: str, password: str, emailID: str):
        """Adds a new user to the database."""
        cur = db.cursor()  # Cursor initialisieren
        try:
            cur.execute('''
                INSERT INTO users (username, password, emailID)
                VALUES (?, ?, ?)
            ''', (username, password, emailID))
            db.commit()
            user_id = cur.lastrowid  # creates a user_id
            print(f"User '{username}' successfully added.")
            return User(user_id, username, password, emailID)
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cur.close()  

    
    # Finds a user
    @staticmethod
    def find_user(db, username: str):
        """Find a user by username."""
        cur = db.cursor()
        try:
            row = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if not row:
                return None
            (user_id, username, password, emailID) = row
            return User(user_id, username, password, emailID)
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cur.close()
 
    # Identefies a user
    @staticmethod
    def username_exists(db, username):
        """Check if a username already exists in the database."""
        cur = db.cursor()
        cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cur.fetchone() is not None
 
 
    # Tries to login a user
    @classmethod
    def try_login(cls, db, username: str, password: str):
        user = cls.find_user(db, username)
        if not user or user.password != password:
            return None
        return user
        
        
     # deletes a user
    def delete_user(self, db):
        """Deletes a user account from the database."""
        self.delete_user_by_name(db, self.username)
        return True
    
 
    # deletes user and userdata 
    @staticmethod
    def delete_user_by_name(db, username):
        cur = db.cursor()
        try:
            cur.execute('''
                DELETE FROM users
                WHERE username = ?
            ''', (username,))
            db.commit()
            if cur.rowcount > 0:
                print(f"Account for '{username}' has been deleted successfully.")
                return True
            else:
                print(f"No account found for '{username}'.")
                return False
        except Exception as e:
            print(f"An error occurred while deleting the account: {e}")
            return False
        finally:
            cur.close()


    
    # creates a list of habits for the user
    def list_habits(self, db):
        """Lists all habits associated with the current user account"""
        return Habit.list_habits_for_user(db, self)


# Database Initialization
def create_tables(db):
    """Create necessary tables in the database."""
    cur = db.cursor()
    
    # Create the users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            emailID TEXT NOT NULL
        )
    ''')
    
    # Create the habits table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            user_id INTEGER NOT NULL,
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            habit_description TEXT,
            start_date DATE,
            end_date DATE,
            habit_type TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    # Create the streaks table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER NOT NULL,
            habit_id INTEGER NOT NULL,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            progress INTEGER DEFAULT 0,
            last_completed DATE,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY(habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE
        )
    ''')
    
    db.commit()

   


# Habit Management
class Habit:
    """Class representing a general habit."""
    def __init__(self, habit_id: int,habit_name: str, habit_description: str, start_date: date, end_date: date, habit_type: str):
        self.habit_id = habit_id
        self.habit_name = habit_name
        self.habit_description = habit_description
        self.start_date = start_date
        self.end_date = end_date
        self.habit_type = habit_type

    # Adds a habit to a user
    @classmethod
    def add_habit(cls, db, user: User, habit_name: str, habit_description: str, start_date: date, end_date: date, habit_type: str):
        user_id = user.user_id
        cur = db.cursor()
        try:
            # checks if user exists
            cur.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
            if not cur.fetchone():
                print(f"Error: User with ID {user_id} does not exist.")
                return None
    
            # checks if habit exists
            cur.execute("SELECT 1 FROM habits WHERE user_id = ? AND habit_name = ?", (user_id, habit_name))
            if cur.fetchone():
                print(f"Error: Habit '{habit_name}' already exists for user ID {user_id}.")
                return None
    
            # adds habit to habit table
            cur.execute('''
                INSERT INTO habits (user_id, habit_name, habit_description, start_date, end_date, habit_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, habit_name, habit_description, start_date, end_date, habit_type))
            db.commit()
            habit_id = cur.lastrowid
            
            # checks if streak exists
            cur.execute("SELECT 1 FROM streaks WHERE user_id = ? AND habit_id = ?", (user_id, habit_id))
            # adds streak to the streak table
            if not cur.fetchone():
                cur.execute('''
                    INSERT INTO streaks (user_id, habit_id, current_streak, longest_streak, progress, last_completed)
                    VALUES (?, ?, 0, 0, 0, NULL)
                ''', (user_id, habit_id))
                db.commit()
            
            print("Good job!")
 
            return habit_id
        except Exception as e:
            print(f"Error adding habit: {e}")
            return None
        finally:
            cur.close()
        

    # Marks a habit as completed and updates the streak
    def complete(self, db, user_id: int):
        """Marks the habit as completed and updates the streak."""
        today = datetime.today().date()
        streak = Streak.get_streak(db, user_id, self.habit_id)
 
        new_streak, changed = self.calculate_streak(today, streak.last_completed, streak.current_streak)
        # Doppelt-geklickt?
        if not changed:
            return streak, False
 
        streak.current_streak = new_streak
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_completed = today
        streak.update_streak(db, user_id, self.habit_id)
        return streak, True


    # Creates a list of all habits for a user
    @classmethod
    def list_habits_for_user(cls, db, user: User):
        """Lists all habits for a given user"""
        raw_habits = db.execute(
            "SELECT habit_id, habit_name, habit_description, start_date, end_date, habit_type FROM habits where user_id = ?",
            (user.user_id,)).fetchall()
        return list(cls._from_raw(raw_habit) for raw_habit in raw_habits)

    # Receives a habit_type, matches the habit_type a value
    @staticmethod
    def _from_raw(raw):
        habit_type = raw[-1]
        match habit_type:
            case "Daily":
                return Daily(*raw[:-1])
            case "Weekly":
                return Weekly(*raw[:-1])
            case "Monthly":
                return Monthly(*raw[:-1])
            case _:
                raise Exception("Invalid habit type")



# Streak Management
class Streak:
    '''Initializes a gerneral Streak class'''
    def __init__(self, current_streak: int, longest_streak: int, last_completed: str):
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.last_completed = last_completed

    # Checks if streak allready exists
    @staticmethod
    def get_streak(db, user_id: int, habit_id: int):
        """Fetches streak data from the database."""
        cur = db.cursor()
        cur.execute('''
            SELECT current_streak, longest_streak, last_completed
            FROM streaks
            WHERE user_id = ? AND habit_id = ?
        ''', (user_id, habit_id))
        result = cur.fetchone()
        cur.close()
        if result:
            return Streak(*result)
        else:
            return Streak(0, 0, None)

    # Updates the streak record in the database
    def update_streak(self, db, user_id: int, habit_id: int):
        """Updates the streak record in the database."""
        cur = db.cursor()
        cur.execute('''
            UPDATE streaks
            SET current_streak = ?, longest_streak = ?, last_completed = ?
            WHERE user_id = ? AND habit_id = ?
        ''', (self.current_streak, self.longest_streak, self.last_completed, user_id, habit_id))
        db.commit()
        cur.close()



# Initializes a Subclass of Habit
class Daily(Habit):
    """Represents a subhabit with a daily period."""

    def __init__(self, habit_id, habit_name, habit_description, start_date, end_date):
        super().__init__(habit_id, habit_name, habit_description, start_date, end_date, habit_type="Daily")
        
    # calculates a streak for a daily habit
    def calculate_streak(self, today: date, last_completed: str, current_streak: int) -> int:
        if not last_completed:
            return 1, True  # Start with 1 if no previous completion
 
        last_date = datetime.strptime(last_completed, "%Y-%m-%d").date()
        diff = (today - last_date).days
        if diff == 0:
            return current_streak, False  # Already completed in period
        elif diff == 1:  # If completed daily
            return current_streak + 1, True
        else:
            return 1, True  # Reset streak




# Initializes a Subclass of Habit
class Weekly(Habit):
    """Represents a subhabit with a weekly period."""
    def __init__(self, habit_id, habit_name, habit_description, start_date, end_date):
        super().__init__(habit_id, habit_name, habit_description, start_date, end_date, habit_type="Weekly")

    # calculates a streak for a weekly habit
    def calculate_streak(self, today: date, last_completed: str, current_streak: int) -> int:
            if not last_completed:
                return 1, True  # Start with 1 if no previous completion
     
            last_date = datetime.strptime(last_completed, "%Y-%m-%d").date()
            diff = (today - last_date).days
            if diff <= 6:
                return current_streak, False  # Already completed in period
            elif diff <= 13:  # If completed daily
                return current_streak + 1, True
            else:
                return 1, True  # Reset streak




# Initializes a Subclass of Habit
class Monthly(Habit):
    """Represents a subhabit with a weekly period."""
    def __init__(self, habit_id, habit_name, habit_description, start_date, end_date):
        super().__init__(habit_id, habit_name, habit_description, start_date, end_date, habit_type="Monthly")

    def calculate_streak(self, today: date, last_completed: str, current_streak: int) -> int:
        if not last_completed:
            return 1, True  # Start with 1 if no previous completion
 
        last_date = datetime.strptime(last_completed, "%Y-%m-%d").date()
        diff = (today.year * 12 + today.month) - (last_date.year * 12 + last_date.month)
        if diff == 0:
            return current_streak, False  # Already completed in period
        elif diff == 1:  # If completed daily
            return current_streak + 1, True
        else:
            return 1, True  # Reset streak

        

# main Execution
def main():
    db = get_db()  # connects to database
    try:
        create_tables(db)  # creates tables

        # Testdata
        if not User.username_exists(db, "user1"):
            User.add_user(db, "user1", hash_password("password123"), "user1@example.com")
            Habit.add_habit(db, 1, "Exercise", "Morning workout", "2025-01-01", "2025-01-31", "Daily")

        # Calls tables and data for an inspectation
        tables = ["users", "habits", "streaks"]
        for table in tables:
            print(f"\n--- Tablecontent: {table} ---")
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, db)
            if df.empty:
                print(f"The table '{table}' is empty.")
            else:
                print(df.to_string(index=False))

    except Exception as e:
        # Errorhandling
        print(f"Es ist ein Fehler aufgetreten: {e}")

    finally:
        close_db(db)  # closes the database

if __name__ == "__main__":
    main()
