import tkinter as tk
from tkinter import filedialog, simpledialog
import PyPDF2

def merge_pdfs():
    paths = filedialog.askopenfilenames(title="Select PDF files to merge", filetypes=[("PDF files", "*.pdf")])
    output = filedialog.asksaveasfilename(defaultextension='.pdf')
        
    pdf_writer = PyPDF2.PdfWriter()
    pdf_output = open(output, 'wb')
    
    for path in paths:
        pdf_reader = PyPDF2.PdfReader(path)
        start_page = simpledialog.askinteger("Input", "Enter the starting page number for " + path, parent=root, minvalue=1)
        if start_page is None:
            start_page = 1
        end_page = simpledialog.askinteger("Input", "Enter the ending page number for " + path, parent=root, minvalue=start_page)
        if end_page is None:
            end_page = len(pdf_reader.pages)
        for page in range(start_page - 1, end_page):
            pdf_writer.add_page(pdf_reader.pages[page])
    
    pdf_writer.write(pdf_output)
    pdf_output.close()

root = tk.Tk()
root.title("Merge PDF Files")


button = tk.Button(root, text="Select PDF Files", command=merge_pdfs)
button.pack()

root.mainloop()