import tkinter as tk
from customtkinter import *
from tkinter import filedialog, scrolledtext
import pandas as pd
from model import Model


def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_label.config(text=f"Selected File: {file_path}")
        process_csv(file_path)

def process_csv(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    # Print the DataFrame to the console
    print(df)
    # Display the DataFrame in the Text widget

    model = Model()
    # Preprocess the DataFrame
    df = model.measure_workload(df)
    display_df(df)

def display_df(df):
    # Clear the Text widget
    text_area.delete('1.0', tk.END)
    # Convert DataFrame to string and insert into Text widget
    text_area.insert(tk.END, df.to_string())

# Create the main window
root = tk.Tk()
root.title("CSV File Upload GUI")
root.geometry("600x400")

# Create and place a button to trigger file upload
upload_button = tk.Button(root, text="Upload CSV File", command=upload_file)
upload_button.pack(pady=10)

# Create and place a label to show the selected file path
file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=10)

# Create a scrolled text widget to display the DataFrame
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
text_area.pack(pady=10)

# Run the application
root.mainloop()
