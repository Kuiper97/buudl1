import tkinter as tk
from tkinter import filedialog,messagebox
import PyPDF2
import os
from PIL import Image, ImageTk

def get_page_ranges(file_listbox, pdf_files, root):
    """Get page ranges for each PDF file"""
    frame = tk.Frame(root)
    frame.pack(pady=10, anchor='w', fill='both', expand=True)

    # Cố định phần bên trái trong suốt quá trình sử dụng rộng 400, cao 300, cho phép expand
    canvas = tk.Canvas(frame, width=400, height=300)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Tạo phần thanh trượt cho phần được cố định bởi canvas phía trên theo trục đứng
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Tạo khung để giữ phần nội dung cho việc chọn input để ghép file pdf
    content_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor='nw')

    entry_fields = []
    new_pdf_files = [file_listbox.get(i) for i in range(file_listbox.size())]
    pdf_files = list(pdf_files)  # Convert tuple to list
    pdf_files.clear()
    pdf_files.extend(new_pdf_files)

    for pdf_file in pdf_files:
        label = tk.Label(content_frame, text=f"Start page muốn ghép của {pdf_file}:", fg="green")
        label.pack(anchor='w', fill='x')
        entry = tk.Entry(content_frame)
        entry.insert(0, "1")  # Set default value to 1
        entry.pack(anchor='w', fill='x')
        entry_fields.append(entry)

        label = tk.Label(content_frame, text=f"End page muốn ghép của {pdf_file}:", fg="blue")
        label.pack(anchor='w', fill='x')
        entry = tk.Entry(content_frame)
        entry.insert(0, str(len(PyPDF2.PdfReader(pdf_file).pages)))  # Set default value to total number of pages
        entry.pack(anchor='w', fill='x')
        entry_fields.append(entry)

    button = tk.Button(content_frame, text="Submit", command=lambda: submit_page_ranges(entry_fields, pdf_files))
    button.pack(anchor='c')

    # Update the scroll region
    content_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

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
        os.startfile(output_file)
    except IOError as e:
        messagebox.showerror("Error", f"Error: {e}")
              
def select_pdf_files(root):
    """Select PDF files to merge"""
    pdf_files = filedialog.askopenfilenames(title="Select PDF files to merge", 
                                            filetypes=[("PDF files", "*.pdf")])
    if not pdf_files:  # Check if the user has selected any files
        return
    # Store the original order of selection
    original_order = list(pdf_files)
    
    # Create a frame to hold the sort button and file list
    frame = tk.Frame(root)
    frame.pack(pady=10, anchor='w', fill='both', expand=True)

    # Create a button to sort the files
    sort_button = tk.Button(frame, text="Sort Files A-Z", command=lambda: sort_files(original_order, frame))
    sort_button.pack(anchor='w', fill='x')

    # Create a label to display the file list
    file_list_label = tk.Label(frame, text="Selected Files:")
    file_list_label.pack(anchor='w', fill='x')

    # Create a frame to hold the file list and scrollbar
    file_list_frame = tk.Frame(frame)
    file_list_frame.pack(anchor='w', fill='both', expand=True)

    # Create a scrollbar for the file list
    scrollbar = tk.Scrollbar(file_list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a listbox to display the file list
    file_listbox = tk.Listbox(file_list_frame, width=160, height=5, yscrollcommand=scrollbar.set)
    file_listbox.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.config(command=file_listbox.yview)
    for file in pdf_files:
        file_listbox.insert(tk.END, file)

    # Create a frame to hold the move up and move down buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(anchor='w', fill='x')

    # Create a button to move the selected file up
    move_up_button = tk.Button(button_frame, text="Move Up", command=lambda: move_file_up(file_listbox))
    move_up_button.pack(side=tk.LEFT)

    # Create a button to move the selected file down
    move_down_button = tk.Button(button_frame, text="Move Down", command=lambda: move_file_down(file_listbox))
    move_down_button.pack(side=tk.LEFT)

    # Create a button to proceed to page range selection
    proceed_button = tk.Button(frame, text="Proceed to Page Range Selection", 
                                command=lambda: get_page_ranges(file_listbox, pdf_files, root))
    proceed_button.pack(anchor='c')

def move_file_up(file_listbox):
    """Move the selected file up in the list"""
    index = file_listbox.curselection()
    if index:
        index = index[0]
        if index > 0:  # Check if the item is not already at the top
            selected_file = file_listbox.get(index)  # Store the selected file
            file_listbox.delete(index)
            file_listbox.insert(index - 1, selected_file)  # Insert the selected file at the new index

def move_file_down(file_listbox):
    """Move the selected file down in the list"""
    index = file_listbox.curselection()
    if index:
        index = index[0]
        if index < file_listbox.size() - 1:  # Check if the item is not already at the bottom
            selected_file = file_listbox.get(index)  # Store the selected file
            file_listbox.delete(index)
            file_listbox.insert(index + 1, selected_file)  # Insert the selected file at the new index

def sort_files(original_order, frame):
    """Sort the files in alphabetical order"""
    pdf_files = sorted(original_order)
    file_listbox = frame.winfo_children()[2]  # Get the listbox widget
    file_listbox.delete(0, tk.END)  # Clear the listbox
    for file in pdf_files:
        file_listbox.insert(tk.END, file)  # Update the listbox with the sorted files

def reset_frames(root):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                child.destroy()
            widget.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("PDF Merger")
    root.iconbitmap("pdf_filetypes_21618.ico")
    root.padding = 10
    root.geometry("1200x500")

    # Add a background image
    image = Image.open("background.png")
    photo = ImageTk.PhotoImage(image)
    background_label = tk.Label(root, image=photo)
    background_label.image = photo  # Keep a reference to the image
    #background_label.pack(fill='both', expand=True)  # Use pack and set fill and expand to True
    background_label.place(relwidth=1, relheight=1)
    # Create a canvas to hold the content
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar and associate it with the canvas
    scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame to hold the content
    content_frame2 = tk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame2, anchor='nw')

    # Create a label to display the title
    title_label = tk.Label(content_frame2, text="PDF Merger", font=("Arial", 20, "bold"), fg="white", bg="#007bff",
                        highlightbackground="#007bff", highlightcolor="#007bff")
    title_label.pack(pady=10, anchor='c', fill='x')

    # Create a label to display the instructions
    instructions_label = tk.Label(content_frame2, text="Select PDF files to merge and enter the page ranges.", fg="blue",
                                highlightbackground="blue", highlightcolor="blue")
    instructions_label.pack(pady=10, anchor='c', fill='x')

    # Create a button to start the merge process
    button = tk.Button(content_frame2, text="Select PDF Files", 
                        command=lambda: select_pdf_files(root))
    button.pack(pady=10, anchor='c')

    # Update the scroll region
    content_frame2.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Add this line to update the scroll region after adding widgets
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Add this line to configure the canvas to expand
    canvas.pack(fill='both', expand=True)
    
    reset_button = tk.Button(content_frame2, text="Reset", fg="white", bg="red", width=5, height=1, font=("Arial", 14, "bold"), padx=10, pady=5, command=lambda: reset_frames(root))
    reset_button.pack(pady=10, anchor='c')

    root.mainloop()