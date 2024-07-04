# import io
# from pathlib import Path
# from tkinter import *
# from tkinter import messagebox
# from PIL import Image, ImageTk
# import imageio
# import threading
# from datetime import datetime
#
# from customtkinter import *
# import sqlite3
#
# from nav import Nav
#
# class SessionManager:
#     logged_in_user_id = None
#
#     @staticmethod
#     def login(user_id):
#         SessionManager.logged_in_user_id = user_id
#
#     @staticmethod
#     def logout():
#         SessionManager.logged_in_user_id = None
#
#     @staticmethod
#     def get_logged_in_user():
#         return SessionManager.logged_in_user_id
#
# # window = gui.getWindow()
#
# class DB:
#     import gui
#     _instance = None  # Class-level attribute to hold the single instance
#     # def __init__(self,window=None):
#
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super(DB, cls).__new__(cls)
#             # Initialize the instance once
#             cls._instance.connection = sqlite3.connect("user_credentials.db")
#             cls._instance.connection.row_factory = sqlite3.Row
#             cls._instance.setup_database()
#             cls._instance.logged_in_user_id = None
#
#         return cls._instance
#
#     @classmethod
#     def setup_database(cls):
#         cursor = cls._instance.connection.cursor()
#         cursor.execute("""
#                             CREATE TABLE IF NOT EXISTS users (
#                                 id INTEGER PRIMARY KEY,
#                                 username TEXT,
#                                 password TEXT
#                             )
#                         """)
#         cursor.execute('''
#                             CREATE TABLE IF NOT EXISTS history (
#                                 session_id INTEGER,
#                                 subject_id INTEGER,
#                                 prediction TEXT,
#                                 image BLOB,
#                                 created_at TEXT,
#                                 created_by INTEGER,
#                                 FOREIGN KEY (created_by) REFERENCES users(id)
#                             )
#                         ''')
#         cls._instance.connection.commit()
#
#     def get_history_data(self):
#         user_id = SessionManager.get_logged_in_user()
#         if user_id is not None:
#             cursor = self.connection.cursor()
#             cursor.execute("SELECT * FROM history WHERE created_by=? ORDER BY session_id", (user_id,))
#             return cursor.fetchall()
#         else:
#             messagebox.showerror("Access Denied", "You must be logged in to perform this operation.")
#             return None
#
#     def close(self):
#         self.connection.close()
#
#
#     def close(self):
#         self.connection.close()
#
#     def get_user_id(self, username):
#         """Retrieve the user ID from the database based on username."""
#         conn = sqlite3.connect("user_credentials.db")
#         c = conn.cursor()
#         c.execute("SELECT id FROM users WHERE username=?", (username,))
#         result = c.fetchone()
#         self.logged_in_user_id = result[0]
#         print(f'userid:{self.logged_in_user_id}')
#         return result[0] if result else None
#
#     def get_next_session_id(self):
#         conn = sqlite3.connect('user_credentials.db')
#         c = conn.cursor()
#         c.execute('SELECT MAX(session_id) FROM history')
#         result = c.fetchone()[0]
#         conn.close()
#         if result is None:
#             return 1  # Return 1 if there are no entries
#         else:
#             return result + 1
#
#     def logout(self):
#         import gui
#         self.window = gui.getWindow()
#         """Handle user logout."""
#         self.logged_in_user_id = None  # Clear the logged-in user's ID
#         # If there are other session-related cleanups, handle them here
#         # Possibly show a message or redirect to a login page
#         messagebox.showinfo("Logged Out", "You have been successfully logged out.")
#         # Redirect to login page or home screen
#         if self.window:
#             self.window.deiconify()  # If the main window was hidden, show it again
#             # Implement additional redirection if needed
#
#     def write_to_hist_table(self, session_id, subject, prediction, img_blob):
#         conn = sqlite3.connect('user_credentials.db')
#         c = conn.cursor()
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         user_id = SessionManager.get_logged_in_user()  # Use the tracked logged-in user ID
#         c.execute(
#             'INSERT INTO history (session_id, subject_id, prediction, image, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)',
#             (session_id, subject, prediction, img_blob, current_time, user_id))
#         conn.commit()
#         conn.close()
#
#     def verify_login(self, username, password):
#         connection = sqlite3.connect("user_credentials.db")
#         cursor = connection.cursor()
#         # Check if the username exists
#         cursor.execute("SELECT password FROM users WHERE username=?", (username,))
#         result = cursor.fetchone()
#         connection.close()
#         if result:
#             # If username exists, check password
#             stored_password = result[0]
#             if stored_password == password:
#                 return "Login successful"
#             else:
#                 return "Incorrect password"
#         return "Username does not exist"
#
#     def login(self, entry_1, entry_2):
#
#         import gui
#         username = entry_1.get()
#         password = entry_2.get()
#         login_result = self.verify_login(username, password)
#         if login_result == "Login successful":
#             # messagebox.showinfo("Login Info", login_result)
#             self.window = gui.getWindow()
#
#             next = Nav(self.window)
#             self.logged_in_user_id = SessionManager.get_logged_in_user()
#             self.window.withdraw()  # Hide the main login window
#             next.open_new_page()  # Open the new page
#         else:
#             messagebox.showerror("Login Info", login_result)
#
#     def sign_up(self,entry_1, entry_2):
#         username = entry_1.get()
#         password = entry_2.get()
#         connection = sqlite3.connect("user_credentials.db")
#         cursor = connection.cursor()
#
#         # Check if the username already exists
#         cursor.execute("SELECT * FROM users WHERE username=?", (username,))
#         if cursor.fetchone():
#             messagebox.showerror("Signup Info", "Username already taken!")
#             connection.close()
#             return
#
#         # If the username doesn't exist, proceed to insert the new user
#         cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
#         connection.commit()
#         connection.close()
#         messagebox.showinfo("Signup Info", "Signup Successful! Please login")
