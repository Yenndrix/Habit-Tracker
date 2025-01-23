# Import necessary modules
import sqlite3
from new_trail import User, Habit, get_db, close_db, create_tables, hash_password, Daily, Weekly, Monthly, Streak


# Adds a user Dashboard
def user_dashboard(db, user):
    """Provide options for the logged-in user to manage their habits."""


    user_id = user.user_id  # Extract user_id from the result

    #provides a Userdashboard
    while True:
        print(f"\nWelcome to your dashboard, {user.username}!")
        print("This Habit Tracker App allows you to:")
        print("1. Create a new habit")
        print("2. Complete an existing habit")
        print("3. Analyze your performance over time")
        print("4. Log out")
        print("5. Delete your account")

        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        # Adds a habit to a user if not exists
        if choice == "1":
            # Create a new habit
            habit_name = input("Please enter habit name: ").strip()
            habit_description = input("Enter habit description: ").strip()
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            habit_type = input("Enter habit type (Daily, Weekly, Monthly): ").strip()

            if habit_type not in ("Daily", "Weekly", "Monthly"):
                print("Invalid habit type. Please choose from Daily, Weekly, or Monthly.")
                continue
                
            # Calls the add_habit method
            habit = Habit.add_habit(
                db,
                user,
                habit_name,
                habit_description,
                start_date,
                end_date,
                habit_type,
            )
            if habit:
                print(f"Habit '{habit_name}' added successfully!")
            else:
                print("Error: Failed to create habit. Please try again.")

        # Mark an existing habit as completed
        elif choice == "2":
            
            habits = user.list_habits(db)
            if not habits:
                print("You haven't created any habits yet.")
                continue
    
                
            #prints a list of habits starting with 1
            print("Your habits:")
            for i, habit in enumerate(habits, start=1):
                print(f"{i}. {habit.habit_name}")  
                
            # Promts the user for input
            habit_choice = input("Enter the number of the habit you want to complete: ").strip() # removes mistakenly added 
            if habit_choice.isdigit():
                habit_index = int(habit_choice) - 1
                if 0 <= habit_index < len(habits):
                    # Mark habit as completed and update the streak
                    habit = habits[habit_index]
                    streak, changed = habit.complete(db, user_id)
                    if changed:
                        print(f"Streak of {habit.habit_name} is now {streak.current_streak}, Longest Streak = {streak.longest_streak}")
                    else:
                        print(f"You already completed {habit.habit_name} this period")
                else:
                    print("Invalid habit number. Please try again.")
            else:
                print("Invalid input. Please enter a valid number.")
        
 
        elif choice == "3":
            print("What would you like to know?")
            print("1. Show me a list of all my habits.")
            print("2. Show me all my habits with the same periodicity. (Daily, Weekly, Monthly)")
            print("3. Show me the longest streak for all of my habits.")
            print("4. Show me the longest streak for a specific habit!")
        
            try:  # Wrap in a try block to catch ValueError
                # Convert input to an integer
                choice_action = int(input("Please choose an action: ").strip())
                    
                if choice_action == 1:
                    # Assuming `user.list_habits` returns a list of habits
                    habits = user.list_habits(db)
                        
                    if not habits:  # If habits is empty
                        print("You haven't created any habits yet.")
                    else:
                        # Prints a list of habits starting with 1
                        print("Your habits:")
                        for i, habit in enumerate(habits, start=1):
                            print(f"{i}. {habit.habit_name}")
                                
                elif choice_action == 2:
                    # Show habits by periodicity
                    periodicity = input("Enter the periodicity (Daily, Weekly, Monthly): ").strip().capitalize()
                    valid_periods = ["Daily", "Weekly", "Monthly"]
                        
                    if periodicity not in valid_periods:
                        print("Invalid periodicity. Please choose from Daily, Weekly, or Monthly.")
                    else:
                        habits = [habit for habit in user.list_habits(db) if habit.habit_type == periodicity]
                            
                        if not habits:
                            print(f"No habits found for periodicity: {periodicity}.")
                        else:
                            print(f"Your {periodicity} habits:")
                            for i, habit in enumerate(habits, start=1):
                                print(f"{i}. {habit.habit_name}")
        
                elif choice_action == 3:
                    # Show the longest streak for all habits
                    habits = user.list_habits(db)
                    
                    if not habits:
                        print("You haven't created any habits yet.")
                    else:
                        print("Longest streaks for all your habits:")
                        for habit in habits:
                            streak = Streak.get_streak(db, user.user_id, habit.habit_id)
                            print(f"Habit: {habit.habit_name}, Longest Streak: {streak.longest_streak}")
        
                elif choice_action == 4:
                    # Show the longest streak for a specific habit
                    habits = user.list_habits(db)
                    
                    if not habits:
                        print("You haven't created any habits yet.")
                    else:
                        print("Your habits:")
                        for i, habit in enumerate(habits, start=1):
                            print(f"{i}. {habit.habit_name}")
                        
                        try:
                            selected_habit_index = int(input("Select the habit number to view the longest streak: ").strip())
                            if 1 <= selected_habit_index <= len(habits):
                                selected_habit = habits[selected_habit_index - 1]
                                streak = Streak.get_streak(db, user.user_id, selected_habit.habit_id)
                                print(f"Habit: {selected_habit.habit_name}, Longest Streak: {streak.longest_streak}")
                            else:
                                print("Invalid habit number.")
                        except ValueError:
                            print("Please enter a valid number.")
                
                else:
                    print("Invalid choice. Please select a valid option.")
            
            except ValueError:  # Handle invalid input for choice_action
                print("Please enter a valid number.")
                    
                      
        elif choice == "4":
            # Log out user
            print(f"Goodbye, {user.username}! You have been logged out.")
            break
        
        elif choice == "5":
            # Delete user account
            delete_choice = input(f"Are you sure you want to delete your account, {user.username}? (yes/no): ").strip().lower()
            if delete_choice == "yes":
                if user.delete_user(db):  
                    print("Your account has been deleted successfully.")
                    break
                else:
                    print("Error: Failed to delete account. Please try again.")
            else:
                print("Account deletion canceled.")                   
                       

# Main CLI function
def cli():
    """Command Line Interface for the Habit Tracking App."""
    print("Welcome to the Habit Tracking App!")

    # Connect to the database
    db = get_db()
    create_tables(db)

    user = None  # Initialize user variable

    # Prompt the user to choose between login or register
    while True:
        if not user:
            # Prompt user for login or register
            choice = input("Do you want to register or login? (login/register): ").lower()
            if choice == "login":
                username = input("Please, enter your username: ")
                password = input("Please, enter your password: ")
                user = User.try_login(db, username, hash_password(password))
                
                if user:
                    print(f"Welcome back, {user.username}!")
                else:
                    print("Error: Can't find this user. Please try again")
                    
            elif choice == "register":
                username = input("Choose a username: ").strip()
                plain_password = input("Choose a password: ").strip()
                email = input("Enter your e-mail: ").strip()

                # Check if the username already exists
                if User.username_exists(db, username):
                    print(f"Error: The username '{username}' is already taken. Please choose a different one.")
                    continue

                hashed_password = hash_password(plain_password)
                
                user = User.add_user(db, username, hashed_password, email)
                if user:
                    print(f"Account for '{username}' created successfully!")
                else:
                    print("Error: process failed. Please try again!")
            else:
                print("Invalid choice. Redirecting to the main menu.")
        else:
            # Provide user with a dashboard
            user_dashboard(db, user)
            user = None  # Logout user after dashboard session
    close_db(db)

if __name__ == "__main__":
    cli()
