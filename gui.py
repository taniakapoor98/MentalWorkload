import subprocess
from pathlib import Path
from tkinter import *
from PIL import Image, ImageTk
import imageio
import threading
from PIL import Image, ImageTk
from customtkinter import *
import os

# def install_packages():
#     packages = ["pandas", "imageio", "matplotlib", "PIL", "mne", "scikit-learn", "nolds"]
#     for package in packages:
#         subprocess.check_call([sys.executable, "-m", "pip", "install", package])
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# Define paths for assets
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = resource_path("./assets/frame0/")
import io
from pathlib import Path
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import imageio
import threading
from datetime import datetime

from customtkinter import *
import sqlite3


class SessionManager:
    logged_in_user_id = None

    @staticmethod
    def login(user_id):
        SessionManager.logged_in_user_id = user_id

    @staticmethod
    def logout():
        SessionManager.logged_in_user_id = None

    @staticmethod
    def set_logged_in_user(user_id):
        SessionManager.logged_in_user_id = user_id

    @staticmethod
    def get_logged_in_user():
        return SessionManager.logged_in_user_id


# window = gui.getWindow()

class DB:
    import gui
    _instance = None  # Class-level attribute to hold the single instance
    # def __init__(self,window=None):

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DB, cls).__new__(cls)
            # Initialize the instance once
            cls._instance.connection = sqlite3.connect("user_credentials.db")
            cls._instance.connection.row_factory = sqlite3.Row
            cls._instance.setup_database()
            cls._instance.logged_in_user_id = None

        return cls._instance

    @classmethod
    def setup_database(cls):
        cursor = cls._instance.connection.cursor()
        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                username TEXT,
                                password TEXT
                            )
                        """)
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS history (
                                session_id INTEGER,
                                subject_id INTEGER,
                                prediction TEXT,
                                created_at TEXT,
                                created_by INTEGER,
                                FOREIGN KEY (created_by) REFERENCES users(id)
                            )
                        ''')
        cls._instance.connection.commit()

    def get_history_data(self):
        user_id = SessionManager.get_logged_in_user()
        if user_id is not None:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM history WHERE created_by=? ORDER BY session_id", (user_id,))
            return cursor.fetchall()
        else:
            messagebox.showerror("Access Denied", "You must be logged in to perform this operation.")
            return None

    def close(self):
        self.connection.close()


    def close(self):
        self.connection.close()

    def get_user_id(self, username):
        """Retrieve the user ID from the database based on username."""
        conn = sqlite3.connect("user_credentials.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (username,))
        result = c.fetchone()
        self.logged_in_user_id = result[0]
        # print(f'userid:{self.logged_in_user_id}')
        return result[0] if result else None

    def get_next_session_id(self):
        conn = sqlite3.connect('user_credentials.db')
        c = conn.cursor()
        c.execute('SELECT MAX(session_id) FROM history')
        result = c.fetchone()[0]
        conn.close()
        if result is None:
            return 1  # Return 1 if there are no entries
        else:
            return result + 1

    def logout(self):
        import gui
        self.window = gui.getWindow()
        """Handle user logout."""
        self.logged_in_user_id = None  # Clear the logged-in user's ID
        # If there are other session-related cleanups, handle them here
        # Possibly show a message or redirect to a login page
        messagebox.showinfo("Logged Out", "You have been successfully logged out.")
        # Redirect to login page or home screen
        if self.window:
            self.window.deiconify()  # If the main window was hidden, show it again
            # Implement additional redirection if needed

    def write_to_hist_table(self, session_id, subject, prediction, img_blob):
        conn = sqlite3.connect('user_credentials.db')
        c = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = SessionManager.get_logged_in_user()  # Use the tracked logged-in user ID
        c.execute(
            'INSERT INTO history (session_id, subject_id, prediction, created_at, created_by) VALUES (?, ?, ?, ?, ?)',
            (session_id, subject, prediction, current_time, user_id))
        conn.commit()
        conn.close()

    def verify_login(self, username, password):
        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()
        # Check if the username exists
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        connection.close()
        if result:
            # If username exists, check password
            stored_password = result[0]
            if stored_password == password:
                return "Login successful"
            else:
                return "Incorrect password"
        return "Username does not exist"

    def login(self, entry_1, entry_2):

        import gui,nav
        username = entry_1.get()
        password = entry_2.get()
        login_result = self.verify_login(username, password)
        if login_result == "Login successful":
            # messagebox.showinfo("Login Info", login_result)
            self.window = window

            next = nav.Nav(self.window)
            SessionManager.set_logged_in_user(self.get_user_id(username))
            self.logged_in_user_id = SessionManager.get_logged_in_user()
            self.window.withdraw()  # Hide the main login window
            next.open_new_page()  # Open the new page
        else:
            messagebox.showerror("Login Info", login_result)

    import sqlite3
    from tkinter import messagebox

    def sign_up(self,entry_1, entry_2):
        username = entry_1.get().strip()  # Using strip() to remove any leading/trailing whitespace
        password = entry_2.get().strip()

        # Check if either the username or password is empty
        if not username or not password:
            messagebox.showerror("Signup Error", "Username and password cannot be empty.")
            return

        # Check if the password length is less than 5 characters
        if len(password) < 5:
            messagebox.showerror("Signup Error", "Password must be at least 5 characters long.")
            return

        connection = sqlite3.connect("user_credentials.db")
        cursor = connection.cursor()

        try:
            # Check if the username already exists
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Signup Info", "Username already taken!")
                return

            # If the username doesn't exist, proceed to insert the new user
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            connection.commit()
            messagebox.showinfo("Signup Info", "Signup Successful! Please login")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            connection.close()


def delete_file( file_path):
    """Delete a file at the specified path."""
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"File {file_path} has been deleted successfully.")
        else:
            print("The file does not exist, and no action was taken.")
    except Exception as e:
        print(f"An error occurred while trying to delete the file: {e}")


def relative_to_assets(path: str):

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, path)

def bttn(x,y,img1,img2,cmd):
    image_a = ImageTk.PhotoImage(Image.open(img1))
    image_b = ImageTk.PhotoImage(Image.open(img2))
    def on_enter(e):
        mybtn['image']=image_b
    def on_leave(e):
        mybtn['image']=image_a
    mybtn=Button(window,image=image_a,
                 border=0,
                 cursor='hand2',
                 command=cmd,
                 relief=FLAT)
    mybtn.bind("<Enter>",on_enter)
    mybtn.bind("<Leave>",on_leave)
    mybtn.place(x=x,y=y)
def login():
    print('logging in')
    db.login(entry_1=entry_1,entry_2=entry_2)
def sign_up():
    print('signing up')
    db.sign_up(entry_1=entry_1, entry_2=entry_2)


def play_video(label, video_path):
    """Function to continuously update video frames in the specified label widget."""
    video = imageio.get_reader(video_path, 'ffmpeg')
    try:
        while True:
            for frame in video.iter_data():
                frame_image = Image.fromarray(frame)
                # Check for the most updated method for resampling
                if hasattr(Image, 'Resampling'):  # New way to access resampling methods in Pillow
                    resample = Image.Resampling.LANCZOS
                else:
                    resample = Image.LANCZOS  # Older versions use direct attributes from Image
                # Resize frame to fit the label's dimensions
                frame_image = frame_image.resize((1000, label.winfo_height()), resample)
                frame_photo = ImageTk.PhotoImage(image=frame_image)
                label.config(image=frame_photo)
                label.image = frame_photo
    except Exception as e:
        print(f"Stopped playing video due to: {e}")
    finally:
        video.close()

window = Tk()
window.geometry("1000x550")
window.configure(bg="#000000")

db = DB()

canvas = Canvas(
    window,
    bg="#010101",  # Changed to match the darker theme if needed
    height=550,
    width=1000,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

# Setup for video playback
video_label = Label(window)
video_label.place(x=0, y=0, width=550, height=550)  # Full left side of the screen

# Other GUI components
image_image_1 = PhotoImage(
    file=resource_path("./assets/frame0/image_1.png"))
image_1 = canvas.create_image(
    500.0,
    275.0,
    image=image_image_1
)

entry_image_1 = PhotoImage(
    file=resource_path("./assets/frame0/entry_1.png"))
entry_bg_1 = canvas.create_image(
    759.0,
    312.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#7B7474",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=645.5,
    y=297.0,
    width=227.0,
    height=34.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("./assets/frame0/entry_2.png"))
entry_bg_2 = canvas.create_image(
    759.0,
    387.5,
    image=entry_image_2
)
entry_2 = Entry(
    window,  # Make sure to place it on the correct parent widget
    bd=0,
    bg="#7B7474",  # Background color of the canvas or window
    fg="#000716",
    highlightthickness=0
    , show="*"
)
entry_2.place(
    x=645.5,
    y=372.0,
    width=227.0,
    height=34.0
)

image_image_2 = PhotoImage(
    file=relative_to_assets("./assets/frame0/image_2.png"))
image_2 = canvas.create_image(
    762.0,
    180.0,
    image=image_image_2
)

canvas.create_text(
    638.0,
    275.0,
    anchor="nw",
    text="Username",
    fill="#FFFFFF",
    font=("Poppins Regular", 14 * -1)
)

canvas.create_text(
    638.0,
    350.0,
    anchor="nw",
    text="Password",
    fill="#FFFFFF",
    font=("Poppins Regular", 14 * -1)
)



bttn(646,425,resource_path("./assets/frame0/button_1.png"),resource_path("./assets/frame0/button.png"),login)

bttn(765,425,resource_path("./assets/frame0/button2.png"),resource_path("./assets/frame0/button2_h.png"),sign_up)



canvas.create_text(
    599.0,
    20.0,
    anchor="nw",
    text="Measure Your Mental Workload",
    fill="#FFFFFF",
    font=("Quicksand Light", 24 * -1)
)
# install_packages()
# Start video playback in a separate thread to keep the UI responsive
thread = threading.Thread(target=play_video, args=(video_label, resource_path(r'.\assets\net.mp4')))
thread.daemon = True
thread.start()

delete_file(resource_path('./workload_meters.pdf'))
window.title('MYMW')
window.resizable(False, False)
window.mainloop()


