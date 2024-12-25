import tkinter as tk
from tkinter import filedialog,messagebox
import PyPDF2
import os
from PIL import Image, ImageTk

import io
import cv2
import numpy as np
from pdf2image import convert_from_path
from tkinter import filedialog, messagebox
#processing
import threading
import time  # Thư viện để mô phỏng thời gian xử lý

#About version
# giảm dpi để giảm dung lượng file

def get_page_ranges(file_listbox, pdf_files, root):
    """Get page ranges for each PDF file"""
    frame = tk.Frame(root)
    frame.pack(pady=10, anchor='w', fill='both', expand=True)

    # Create a canvas to hold the content
    canvas = tk.Canvas(frame, width=400, height=300)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a scrollbar and associate it with the canvas
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
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
    dpi_entry.insert(0, "150")  # Giá trị mặc định
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

def process_pdfs(entry_fields, pdf_files, target_dpi, page_ranges):
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
    processing_thread = threading.Thread(target=process_pdfs, args=(entry_fields, pdf_files, target_dpi, page_ranges))
    processing_thread.start()



def preprocess_scanned_pdf(input_pdf_path, output_pdf_path, target_dpi):
    """
    Xử lý tối ưu PDF scan trước khi merge
    Các bước xử lý:
    1. Chuyển đổi PDF sang ảnh
    2. Xử lý nâng cao chất lượng ảnh
    3. Nén và giảm độ phân giải
    4. Tạo PDF mới
    """
    try:
        # Chuyển đổi PDF sang ảnh
        images = convert_from_path(
            input_pdf_path, 
            dpi=target_dpi,
            grayscale=False
        )
        
        processed_images = []
        
        for img in images:
            # Chuyển ảnh PIL sang numpy
            np_image = np.array(img)
            
            # Các kỹ thuật xử lý ảnh scan
            # 1. Khử nhiễu Grayscale
            #denoised = cv2.fastNlMeansDenoising(np_image, None, 10, 7, 21)
            # 1. Khử nhiễu Color
            denoised = cv2.fastNlMeansDenoisingColored(np_image, None, 10, 7, 21)
            
            # 2. Điều chỉnh độ tương phản - Grayscale
            #clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            #contrast_enhanced = clahe.apply(denoised)
            
            # 2. Điều chỉnh độ tương phản - color 
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            contrast_enhanced = clahe.apply(cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY))  # Chuyển đổi sang grayscale để điều chỉnh độ tương phản
            
            
            # 3. Chỉnh sáng
            brightness_adjusted = cv2.convertScaleAbs(contrast_enhanced, alpha=1.2, beta=10)
            
            # 4. Làm sắc nét
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(brightness_adjusted, -1, kernel)
            
            # Chuyển lại sang ảnh PIL
            pil_image = Image.fromarray(sharpened)
            
            # Nén ảnh
            buffered = io.BytesIO()
            pil_image.save(
                buffered, 
                format='JPEG', 
                optimize=True, 
                quality=60  # Điều chỉnh chất lượng nén
            )
            
            processed_images.append(Image.open(buffered))
        
        # Lưu PDF
        first_image = processed_images[0]
        other_images = processed_images[1:]
        
        first_image.save(
            output_pdf_path, 
            "PDF", 
            resolution=target_dpi, 
            save_all=True, 
            append_images=other_images
        )
        
        return True
    
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể xử lý PDF scan: {str(e)}")
        return False

def merge_pdfs(pdf_files, page_ranges, target_dpi):
    """Merge PDFs and optimize scanned PDFs"""
    # Danh sách PDF đã xử lý
    processed_pdf_files = []
    
    # Xử lý từng file PDF scan trước khi merge
    for pdf_file in pdf_files:
        # Tạo file tạm để lưu PDF đã xử lý
        processed_pdf_path = f"processed_{os.path.basename(pdf_file)}"
        
        # Xử lý PDF scan
        if preprocess_scanned_pdf(pdf_file, processed_pdf_path, target_dpi):
            processed_pdf_files.append(processed_pdf_path)
        else:
            # Nếu xử lý lỗi, sử dụng file gốc
            processed_pdf_files.append(pdf_file)
    
    # Thực hiện merge như bình thường
    output_file = filedialog.asksaveasfilename(defaultextension='.pdf')
    if not output_file:
        return

    pdf_writer = PyPDF2.PdfWriter()

    for pdf_file, (start_page, end_page) in zip(processed_pdf_files, page_ranges):
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

    # Lưu file merge
    with open(output_file, 'wb') as pdf_output:
        pdf_writer.write(pdf_output)

    # Xóa các file PDF tạm
    for temp_file in processed_pdf_files:
        if temp_file.startswith("processed_"):
            os.remove(temp_file)

    # Mở file PDF đã merge
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
    # Tạo một nhãn để hiển thị icon
    icon_image = Image.open("cooperation_puzzle_icon_262690.ico")  # Tải hình ảnh
    icon_photo = ImageTk.PhotoImage(icon_image)  # Chuyển đổi hình ảnh thành PhotoImage

    icon_label = tk.Label(content_frame2, image=icon_photo)  # Tạo nhãn với hình ảnh
    icon_label.image = icon_photo  # Giữ tham chiếu đến hình ảnh
    icon_label.pack(pady=10, anchor='c')  # Đặt nhãn dưới nút reset_button

    root.mainloop()