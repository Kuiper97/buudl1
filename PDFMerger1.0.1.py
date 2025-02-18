from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog,messagebox
import PyPDF2
import os
from PIL import Image, ImageTk
from io import BytesIO
from pdf2image import convert_from_path
from tkinter import filedialog, messagebox
#processing
import threading
import time  # Thư viện để mô phỏng thời gian xử lý

#About version
# giảm dpi để giảm dung lượng file

def get_page_ranges(file_listbox, pdf_files, root):
    """Get page ranges for each PDF file"""
    rb_frame = tk.Frame(root)
    rb_frame.pack(pady=10, anchor='w', fill='both', expand=True)

    # Create a canvas to hold the content
    canvas = tk.Canvas(rb_frame, width=400, height=300)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar and associate it with the canvas
    scrollbar = tk.Scrollbar(rb_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame to hold the content
    content_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor='nw')

    entry_fields = []
    new_pdf_files = [file_listbox.get(i) for i in range(file_listbox.size())]
    pdf_files = list(pdf_files)  # Convert tuple to list
    pdf_files.clear()
    pdf_files.extend(new_pdf_files)
    # Thêm ô nhập cho target_dpi
    dpi_label = tk.Label(content_frame, text="Nhập target DPI:", fg="blue")
    dpi_label.pack(anchor='w', fill='x')
    dpi_entry = tk.Entry(content_frame)
    dpi_entry.insert(0, "300")  # Giá trị mặc định
    dpi_entry.pack(anchor='w', fill='x')

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

    # Tạo nút Submit
    button = tk.Button(content_frame, text="Submit", command=lambda: submit_page_ranges(entry_fields, pdf_files, dpi_entry))
    button.pack(anchor='c')

    # Update the scroll region
    content_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

def process_pdfs(pdf_files, target_dpi, page_ranges):
    """Hàm xử lý PDF trong một luồng riêng"""
    
    # Tạo frame cho thông báo loading
    loading_frame = tk.Frame(content_frame2, bg="blue")
    loading_frame.pack(side=tk.BOTTOM, pady=10, padx=20, fill='x')
    
    # Hiển thị thông báo loading
    loading_label = tk.Label(loading_frame, text="Processing... Please wait.", fg="white", bg="blue", font=("Arial", 16, "bold"))
    loading_label.pack(pady=20)
    # Cập nhật kích thước của canvas
    content_frame2.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Giả lập thời gian xử lý (thay thế bằng mã xử lý PDF thực tế)
    # Thay thế bằng hàm xử lý PDF của bạn
    time.sleep(3)

    # Gọi hàm merge_pdfs hoặc hàm xử lý PDF của bạn
    merge_pdfs(pdf_files, page_ranges, target_dpi)

    # Ẩn thông báo loading sau khi hoàn tất
    loading_frame.pack_forget()
    messagebox.showinfo("Info", "Processing completed!")
    
def submit_page_ranges(entry_fields, pdf_files, dpi_entry):
    """Submit page ranges and merge PDFs"""
    page_ranges = []
    try:
        target_dpi = int(dpi_entry.get())  # Lấy giá trị từ ô nhập và chuyển đổi thành số nguyên
    except ValueError:
        messagebox.showerror("Error", "Invalid DPI value")
        return

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

    # Tạo một luồng mới để xử lý PDF
    processing_thread = threading.Thread(target=process_pdfs, args=(pdf_files, target_dpi, page_ranges))
    processing_thread.start()


def preprocess_scanned_pdf(input_pdf_path, output_pdf_path, target_dpi):
    """Xử lý tối ưu PDF scan trước khi merge bằng cách giảm DPI"""
    try:
        # Convert PDF to images with specified DPI
        images = convert_from_path(input_pdf_path, dpi=target_dpi)

        # Use a ThreadPoolExecutor for concurrent processing of images
        with ThreadPoolExecutor() as executor:
            image_list = list(executor.map(process_image, images))

        # Save all images to a single PDF
        if image_list:
            first_image = image_list[0]
            other_images = image_list[1:]
            first_image.save(output_pdf_path, "PDF", resolution=target_dpi, save_all=True, append_images=other_images)

        return True

    except Exception as e:
        print(f"Không thể xử lý PDF scan: {str(e)}")
        return False

def process_image(image):
    """Process a single image (e.g., convert to desired format)"""
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')  # Save as JPEG in memory
    img_byte_arr.seek(0)  # Move to the beginning of the BytesIO object
    return Image.open(img_byte_arr)

def merge_pdfs(pdf_files, page_ranges, target_dpi):
    """Merge PDFs and optimize scanned PDFs"""
    processed_pdf_files = []
    
    for pdf_file in pdf_files:
        processed_pdf_path = f"processed_{os.path.basename(pdf_file)}"
        
        if preprocess_scanned_pdf(pdf_file, processed_pdf_path, target_dpi):
            processed_pdf_files.append(processed_pdf_path)
        else:
            processed_pdf_files.append(pdf_file)

    output_file = filedialog.asksaveasfilename(defaultextension='.pdf')
    if not output_file:
        messagebox.showinfo("Info", "No output file selected. Operation cancelled.")
        return

    pdf_writer = PyPDF2.PdfWriter()

    for pdf_file, (start_page, end_page) in zip(processed_pdf_files, page_ranges):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            if start_page < 1 or end_page > total_pages:
                messagebox.showerror("Error", f"Page range {start_page}-{end_page} is out of bounds for {pdf_file}.")
                return
            
            for page in range(start_page - 1, end_page):
                pdf_writer.add_page(pdf_reader.pages[page])

        except PyPDF2.PdfReader.PdfReadError as e:
            messagebox.showerror("Error", f"Error reading PDF file: {e}")
            return

    try:
        with open(output_file, 'wb') as pdf_output:
            pdf_writer.write(pdf_output)
    finally:
        for temp_file in processed_pdf_files:
            if temp_file.startswith("processed_"):
                os.remove(temp_file)

    os.startfile(output_file)
              
def select_pdf_files(root):
    """Select PDF files to merge"""
    pdf_files = filedialog.askopenfilenames(title="Select PDF files to merge", 
                                            filetypes=[("PDF files", "*.pdf")])
    if not pdf_files:  # Check if the user has selected any files
        return
    # Store the original order of selection
    original_order = list(pdf_files)
    
    # Create a frame to hold the sort button and file list
    rt_frame = tk.Frame(root)
    rt_frame.pack(pady=10, anchor='w', fill='both', expand=True)

    # Create a button to sort the files
    sort_button = tk.Button(rt_frame, text="Sort Files A-Z", command=lambda: sort_files(original_order, rt_frame))
    sort_button.pack(anchor='w', fill='x')

    # Create a label to display the file list
    file_list_label = tk.Label(rt_frame, text="Selected Files:", highlightcolor='blue')
    file_list_label.pack(anchor='w', fill='x')

    # Create a frame to hold the file list and scrollbar
    file_list_frame = tk.Frame(rt_frame)
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
    button_frame = tk.Frame(rt_frame)
    button_frame.pack(anchor='w', fill='x')

    # Create a button to move the selected file up
    move_up_button = tk.Button(button_frame, text="Move Up", command=lambda: move_file_up(file_listbox))
    move_up_button.pack(side=tk.LEFT)

    # Create a button to move the selected file down
    move_down_button = tk.Button(button_frame, text="Move Down", command=lambda: move_file_down(file_listbox))
    move_down_button.pack(side=tk.LEFT)

    # Create a button to proceed to page range selection
    proceed_button = tk.Button(rt_frame, text="Proceed to Page Range Selection", 
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
    root.geometry("1200x600")

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
    title_label = tk.Label(content_frame2, text="PDF Merger", font=("Arial", 20, "bold"), fg="red",
                        highlightbackground="blue", highlightcolor="blue")
    title_label.pack(pady=10, anchor='c', fill='x')

    # Create a label to display the instructions
    instructions_label = tk.Label(content_frame2, text="Select PDF files to merge and enter the page ranges.", fg="blue",
                                highlightbackground="blue", highlightcolor="blue")
    instructions_label.pack(pady=10, anchor='c', fill='x')

    # Create a button to start the merge process
    button = tk.Button(content_frame2, text="Select PDF Files", command=lambda: select_pdf_files(root))
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
    # Tạo một nhãn để hiển thị icon
    icon_image = Image.open("cooperation_puzzle_icon_262690.ico")  # Tải hình ảnh
    icon_photo = ImageTk.PhotoImage(icon_image)  # Chuyển đổi hình ảnh thành PhotoImage

    icon_label = tk.Label(content_frame2, image=icon_photo)  # Tạo nhãn với hình ảnh
    icon_label.image = icon_photo  # Giữ tham chiếu đến hình ảnh
    icon_label.pack(pady=10, anchor='c')  # Đặt nhãn dưới nút reset_button
    
    copyright_frame = tk.Frame(content_frame2)
    copyright_frame.pack(side=tk.BOTTOM, pady=10, anchor='c')

    # Create a label for the copyright notice
    copyright_label = tk.Label(copyright_frame, text="© 2024 by Đoàn Lương Bửu", fg="gray", font=("Arial", 10))
    copyright_label.pack()

    root.mainloop()