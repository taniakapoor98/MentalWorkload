import glob
import os
import shutil
import sys
import time
from tkinter import *
from tkinter import filedialog, messagebox

import PIL
import pandas as pd
from PIL import Image, ImageTk
import threading
import imageio
from tkinter import filedialog
from model import Model

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



class Home:

    def __init__(self, main_fm):
        self.file_uploaded = False
        self.main_fm = main_fm
        self.home_page_fm = Frame(self.main_fm, bg='black')  # Set the background to match the video
        self.home_page_fm.pack(fill=BOTH, expand=True)
        self.create_wid()
        # Set up the video
        video_label = Label(self.home_page_fm)
        video_label.place(x=0, y=0, width=1000, height=550)  # Adjust width and height as needed
        thread = threading.Thread(target=self.play_video, args=(video_label, resource_path(r'.\assets\brainvid2.mp4')))
        thread.daemon = True
        thread.start()


        # Button 1
        button_image_1 = PhotoImage(file=resource_path('./assets/frame0/home/button_1.png'))
        button_1 = Button(self.home_page_fm, image=button_image_1, borderwidth=0,
                          highlightthickness=0, command=self.upload_file, relief="flat", cursor='hand2')
        button_1.place(x=133, y=313, width=144, height=37)
        button_1.image = button_image_1  # Keep a reference

        # Button 2
        button_image_2 = PhotoImage(file=resource_path('./assets/frame0/home/button_2.png'))
        button_2 = Button(self.home_page_fm, image=button_image_2, borderwidth=0,
                          highlightthickness=0, command=self.process_csv, relief="flat",cursor='hand2')
        button_2.place(x=290, y=313, width=144, height=37)
        button_2.image = button_image_2  # Keep a reference

        bg_text = Label(self.home_page_fm, bg='white')
        bg_text.place(x=106.0, y=249.0, width=365.0, height=55.0)
        self.file_label = Label(self.home_page_fm, text="No file selected", bg='white',fg='black')
        self.file_label.place(x=120, y=270.5)
        # self.file_label.pack(pady=10)

        # Additional image 2
        image_image_2 = PhotoImage(file=resource_path('./assets/frame0/home/image_2.png'))
        image_2 = Label(self.home_page_fm, image=image_image_2,bd=0)
        image_2.place(x=500, y=30)
        image_2.image = image_image_2  # Keep a reference
        image_2.lift()

        #viewer window
        self.right_frame = Frame(self.home_page_fm, bg='black')
        self.right_frame.place(x=504, y=34, width=385, height=450)
        self.gif_path = resource_path('./assets/loading.gif')
        self.img = Image.open(self.gif_path)
        self.frame_count = self.img.n_frames
        self.stop_animation = False
        # Optional: Adding a label inside the frame to demonstrate usage
        self.label = Label(self.right_frame, text="Upload file to get started", bg='black', fg='gray')
        self.label.pack(expand=True, fill='both')

        button_3 = Button(self.home_page_fm, text='Download', borderwidth=0,
                          highlightthickness=0, command=self.save_file_as, cursor='hand2',relief="flat",bg='black',fg='white', activebackground='gray')
        button_3.place(x=900, y=50, width=90, height=23)



    def load_pdf(self, file_path):
        import fitz  # PyMuPDF
        from PIL import Image, ImageTk

        doc = fitz.open(file_path)
        pages = [page.get_pixmap() for page in doc]
        images = []
        for p in pages:
            img = Image.frombytes("RGB", [p.width, p.height], p.samples)
            img = img.resize((385, int(img.height * (385 / p.width))))  # Adjust size
            images.append(img)
        return images

    def setup_scrollable_canvas(self,root):
        """ Create a scrollable canvas in the given root widget. """
        canvas = Canvas(self.right_frame)
        scrollbar = Scrollbar(self.right_frame, command=canvas.yview)
        scrollable_frame = Frame(canvas)

        # Configure canvas and scrollbar
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Layout the canvas and scrollbar

        canvas.place(x=0, y=0, width=385, height=450)
        scrollbar.place(x=370, y=0, height=450)

        # Ensure the scrollregion is updated when the size of the frame changes
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        return canvas, scrollable_frame
    def view_file(self):

        file_path = resource_path(r'.\workload_meters.pdf')
        root = self.right_frame

        images = self.load_pdf(file_path)

        # Setup scrollable canvas
        canvas, frame = self.setup_scrollable_canvas(root)

        # Display each page image in the scrollable frame
        for img in images:
            photo = ImageTk.PhotoImage(img)
            label = Label(frame, image=photo)
            label.image = photo  # keep a reference!
            label.pack()

    def save_file_as(self):
        """Prompts the user to save a PDF file to a new location with a default filename."""
    # Path to your existing PDF file
        source_path = resource_path('.\workload_meters.pdf')  # Update this path to your PDF file

        # Ask the user for a location and filename to save the PDF file, with a default filename
        target_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="workload_data.pdf"  # Default filename provided here
        )

        # Check if the user has selected a file path
        if target_path:
            try:
                # Copy the file to the new location
                shutil.copy(source_path, target_path)
                messagebox.showinfo("Success", f"The PDF file has been saved as: {target_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save the PDF file: {e}")
        else:
            messagebox.showinfo("Cancelled", "File save operation cancelled.")
    def upload_file(self):
        self.delete_file('workload_meters.pdf')
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

        if self.file_path:
            self.file_label.config(text=f"Selected File: {self.file_path}")
            # self.process_csv(file_path)
            self.file_uploaded = True

    def delete_file(self,file_path):
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
    ## code from https://youtu.be/A9mxZGV_zmI?si=B2Gg8ZzxKimDAGX_
    # def _get_frames(self,img):
    #
    # def _next_frames(self, frame,label,frames,restart=False):
    #
    # def _play_gif(self, label,frames):

    def create_wid(self):
        pass

    def button_command(self):
        # time.sleep(5)
        try:
            self.label.config(text=f"Processing...")
            self.label.update()
            self.show_results('results')
        except Exception as e:
            print(f"Error: {e}")

    def show_results(self,result):
        for child in self.right_frame.winfo_children():
            child.destroy()
        results_label = Label(self.right_frame,bg='white',bd=0,highlightthickness=0,text=result)
        results_label.grid(column=0,row=0)
    ## end
    def process_csv(self):

        # Read the CSV file into a DataFrame
        if self.file_uploaded:
            self.button_command()
            df = pd.read_csv(self.file_path)
            # Print the DataFrame to the console
            print(df)
            # Display the DataFrame in the Text widget

            model = Model()
            # Preprocess the DataFrame
            df = model.measure_workload(df)
            self.view_file()
        else:
            messagebox.showerror("File error", "Please upload a file first")

        # display_df(df)

    def display_image(self, label, image_path):
        """Function to display a static image in the specified label widget."""
        try:
            img = Image.open(image_path)
            img = img.resize((392, 458), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo  # Keep a reference
        except Exception as e:
            print(f"Failed to load image: {e}")


    def play_video(self,label, video_path):
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