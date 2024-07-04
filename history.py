import io
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import gui

class Hist:
    def __init__(self, main_fm):
          # Ensure this module is correctly imported
        self.main_fm = main_fm
        self.hist_page_fm = tk.Frame(self.main_fm)
        self.hist_page_fm.pack(fill=tk.BOTH, expand=True)

        # self.tree = ttk.Treeview(self.hist_page_fm)
        style = ttk.Style()
        style.theme_use("default")  # Can be 'clam', 'alt', 'default', 'classic', or other available themes
        style.configure("Treeview.Heading", background="black", foreground="white", font=('Calibri', 10, 'bold'))

        self.tree = ttk.Treeview(self.hist_page_fm, style="Treeview")
        # self.tree.
        # Define the columns that don't need to display the image directly in the tree
        self.tree["columns"] = ("subject_id", "prediction", "created_at")
        self.tree.heading("#000000", text="Session ID", anchor="w")
        self.tree.heading("subject_id", text="Subject ID")
        self.tree.heading("prediction", text="Prediction")
        self.tree.heading("created_at", text="Created At")

        self.tree.column("#0", anchor="w", width=100)
        self.tree.column("subject_id", anchor="center", width=100)
        self.tree.column("prediction", anchor="center", width=100)
        self.tree.column("created_at", anchor="center", width=150)


        self.load_data()
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Image display area
        # self.image_label = tk.Label(self.hist_page_fm)
        # self.image_label.pack(fill=tk.BOTH, expand=True)
    def get_history_data(self):
        user_id = gui.SessionManager.get_logged_in_user()

        if user_id is not None:
            conn = sqlite3.connect('user_credentials.db')
            conn.row_factory = sqlite3.Row

            c = conn.cursor()
            c.execute("SELECT * FROM history WHERE created_by=? ORDER BY session_id", (user_id,))
            return c.fetchall()
        else:
            messagebox.showerror("Access Denied", "You must be logged in to perform this operation.")
            return None
    def load_data(self):
        history_data = self.get_history_data()
        for r in history_data:
            print(r)
        current_session = None
        parent = ''
        i = 0

        for row in history_data:
            i+=1
            session_id = row['session_id']
            if session_id != current_session:
                parent = self.tree.insert("", "end", text=f"SessionId: {session_id}", open=False)
                current_session = session_id
            # Include session_id and an actual database row_id if available
            self.tree.insert(parent, "end", text="", values=(
            row["subject_id"], row["prediction"], row["created_at"], row["session_id"], session_id))

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, "values")
        # Ensure that the indices match how you've inserted the data
        # row_id = item_values[1]  # Assuming row_id is the fourth element
        # session_id = item_values[0]  # Assuming session_id is the fifth element
    #
    #     self.display_image(row_id)  # Assuming this method needs the row_id to fetch image
    #     print(f'row_id: {row_id}, session_id: {session_id}, item:{item_values}')
    # def get_image(self, subject_id,session_id):
    #     # Fetch the binary image data based on subject_id from the history table
    #     cursor = self.db.connection.cursor()
    #     cursor.execute("SELECT image FROM history WHERE subject_id=? and session_id=?", (subject_id,session_id))
    #     result = cursor.fetchone()
    #     if result:
    #         return result['image']
    #     return None

    # def display_image(self, subject_id, session_id):
    #     image_data = self.get_image(subject_id,session_id)
    #     if image_data:
    #         image = Image.open(io.BytesIO(image_data))
    #
    #         # Resize the image
    #         # Assuming you want the image to be resized to fit a specific size, e.g., 300x300 pixels
    #         image = image.resize((50, 20))  # Use ANTIALIAS to smooth scaling
    #         # Convert the image to a PhotoImage
    #         photo = ImageTk.PhotoImage(image)
    #
    #         # Display the image in the label
    #         self.image_label.config(image=photo)
    #         self.image_label.image = photo  # Keep a reference to prevent garbage collection
    #     else:
    #         messagebox.showinfo("Error", "No image available for this record.")



