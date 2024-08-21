import tkinter as tk
from tkinter import filedialog,messagebox
import PyPDF2
import os


def get_page_ranges(pdf_files, root):
    """Get page ranges for each PDF file"""
    frame = tk.Frame(root)
    frame.pack(pady=10, anchor='w', fill='both', expand=True)
    entry_fields = []

    for pdf_file in pdf_files:
        label = tk.Label(frame, text=f"Start page muốn ghép của {pdf_file}:", fg="green")
        label.pack(anchor='w', fill='x')
        entry = tk.Entry(frame)
        entry.insert(0, "1")  # Set default value to 1
        entry.pack(anchor='w', fill='x')
        entry_fields.append(entry)

        label = tk.Label(frame, text=f"End page muốn ghép của {pdf_file}:", fg="blue")
        label.pack(anchor='w', fill='x')
        entry = tk.Entry(frame)
        entry.insert(0, str(len(PyPDF2.PdfReader(pdf_file).pages)))  # Set default value to total number of pages
        entry.pack(anchor='w', fill='x')
        entry_fields.append(entry)

    button = tk.Button(frame, text="Submit", command=lambda: submit_page_ranges(entry_fields, pdf_files))
    button.pack(anchor='c')

def submit_page_ranges(entry_fields, pdf_files):
    """Submit page ranges and merge PDFs"""
    page_ranges = []
    for i in range(0, len(entry_fields), 2):
        start_page_entry = entry_fields[i]
        end_page_entry = entry_fields[i+1]
        try:
            start_page = int(start_page_entry.get())
            end_page = int(end_page_entry.get())
            if start_page > end_page:
                raise ValueError("Invalid page range")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid page range: {e}")
            return
        page_ranges.append((start_page, end_page))

    merge_pdfs(pdf_files, page_ranges)

def merge_pdfs(pdf_files, page_ranges):
    """Merge PDFs"""
    output_file = filedialog.asksaveasfilename(defaultextension='.pdf')
    if not output_file:
        return

    pdf_writer = PyPDF2.PdfWriter()

    for pdf_file, (start_page, end_page) in zip(pdf_files, page_ranges):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in range(start_page - 1, end_page):
                if page < len(pdf_reader.pages):  # Check if the page exists
                    pdf_writer.add_page(pdf_reader.pages[page])
                else:
                    messagebox.showerror("Error", f"Page {page + 1} does not exist in {pdf_file}")
                    return
        except PyPDF2.PdfReader.PdfReadError as e:
            messagebox.showerror("Error", f"Error reading PDF file: {e}")
            return

    try:
        with open(output_file, 'wb') as pdf_output:
            pdf_writer.write(pdf_output)
    except IOError as e:
        messagebox.showerror("Error", f"Error: {e}")
              
def select_pdf_files(root):
    """Select PDF files to merge"""
    pdf_files = filedialog.askopenfilenames(title="Select PDF files to merge", 
                                            filetypes=[("PDF files", "*.pdf")])
    if not pdf_files:  # Check if the user has selected any files
        return
    get_page_ranges(pdf_files, root)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("PDF Merger")
    root.iconbitmap("pdf_filetypes_21618.ico")
    root.padding = 10
    root.geometry("1000x500")

    # Create a label to display the title
    title_label = tk.Label(root, text="PDF Merger", font=("Arial", 20, "bold"), fg="red",
                        highlightbackground="blue", highlightcolor="blue")
    title_label.pack(pady=10, anchor='c', fill='x')

    # Create a label to display the instructions
    instructions_label = tk.Label(root, text="Select PDF files to merge and enter the page ranges.", fg="blue",
                                highlightbackground="blue", highlightcolor="blue")
    instructions_label.pack(pady=10, anchor='c', fill='x')

    # Create a button to start the merge process
    button = tk.Button(root, text="Select PDF Files", 
                        command=lambda: select_pdf_files(root))
    button.pack(pady=10, anchor='c')

    root.mainloop()