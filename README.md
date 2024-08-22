# buudl1
Chuyển Đổi Từ File Python -> .exe

Để chuyển đổi một file Python sang định dạng thực thi (.exe) trên Windows, bạn có thể sử dụng công cụ pyinstaller. Dưới đây là các bước để thực hiện điều này:

Cài đặt PyInstaller: Đầu tiên, bạn cần cài đặt PyInstaller. Bạn có thể làm điều này bằng cách mở Terminal hoặc Command Prompt và chạy lệnh sau:

pip install pyinstaller

Chuyển đổi file Python sang .exe: Sau khi đã cài đặt PyInstaller, bạn có thể sử dụng nó để chuyển đổi file Python của mình thành một file .exe. Để làm điều này, hãy mở Terminal hoặc Command Prompt, điều hướng đến thư mục chứa file Python của bạn và chạy lệnh sau:

pyinstaller --onefile your_script.py

pyinstaller --onefile --icon=your_icon.ico your_script.py

khi không muốn chạy thêm console when run: 
pyinstaller --noconsole --icon=pdf_filetypes_21618.ico ghep_file_pdf_ver2.py


Trong đó, your_script.py là tên của file Python bạn muốn chuyển đổi. Lệnh trên sẽ tạo ra một file .exe trong thư mục dist trong thư mục hiện tại.

Lưu ý: Nếu mã nguồn của bạn sử dụng các thư viện không phải là phần của thư viện chuẩn Python, bạn cần đảm bảo rằng tất cả các thư viện này cũng đã được cài đặt trên máy tính nơi bạn chạy PyInstaller. <<<<<<< HEAD