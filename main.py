import tkinter as tk
from tkinter import ttk, messagebox
import ctypes




# ================= C LIBRARY CONNECTION ================= #


lib = ctypes.CDLL("./library.dll")

lib.initializeLibrary.argtypes = []
lib.initializeLibrary()


# Define argument and return types
lib.addBook.argtypes = [ctypes.c_int,
                        ctypes.c_char_p,
                        ctypes.c_char_p,
                        ctypes.c_int]

lib.displayBooks.argtypes = [ctypes.c_char_p]

lib.searchBook.argtypes = [ctypes.c_int,
                           ctypes.c_char_p]
lib.searchBook.restype = ctypes.c_int

lib.deleteBook.argtypes = [ctypes.c_int]
lib.deleteBook.restype = ctypes.c_int

lib.undoDelete.argtypes = []

lib.issueBook.argtypes = [ctypes.c_int]

lib.returnBook.restype = ctypes.c_int

# ================= MAIN WINDOW ================= #

root = tk.Tk()
root.title("Library Management System")
root.geometry("1000x600")
root.configure(bg="#e6e6e6")

# ================= HEADER ================= #

header = tk.Label(root, text="📚 Library Management System",
                  bg="#2e8b57", fg="white",
                  font=("Arial", 22, "bold"), pady=15)
header.pack(fill="x")

# ================= SIDEBAR ================= #

sidebar = tk.Frame(root, bg="#d9d9d9", width=200)
sidebar.pack(side="left", fill="y")

# ================= CONTENT AREA ================= #

content = tk.Frame(root, bg="white")
content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ================= FUNCTIONS ================= #

def add_book():
    title = entry_title.get()
    author = entry_author.get()
    quantity = entry_quantity.get()

    if title == "" or author == "" or quantity == "":
        messagebox.showerror("Error", "All fields are required")
        return

    lib.addBook(
        0,  # ID handled internally in C if implemented
        title.encode(),
        author.encode(),
        int(quantity)
    )

    messagebox.showinfo("Success", "Book Added Successfully")

    entry_title.delete(0, tk.END)
    entry_author.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)

    show_books()


def show_books():
    for row in tree.get_children():
        tree.delete(row)

    buffer = ctypes.create_string_buffer(5000)
    lib.displayBooks(buffer)

    data = buffer.value.decode()

    if data.strip() == "":
        return

    lines = data.strip().split("\n")

    for line in lines:
        parts = line.split("|")
        if len(parts) >= 4:
            tree.insert("", tk.END, values=parts)


def delete_selected():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a book to delete")
        return

    values = tree.item(selected, "values")
    book_id = int(values[0].replace("ID:", "").strip())

    result = lib.deleteBook(book_id)

    if result:
        messagebox.showinfo("Success", "Book Deleted (Undo Available)")
        show_books()
    else:
        messagebox.showerror("Error", "Book Not Found")


def undo_delete():
    lib.undoDelete()
    messagebox.showinfo("Success", "Undo Successful")
    show_books()


def issue_book():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a book to issue")
        return

    values = tree.item(selected, "values")
    book_id = int(values[0].replace("ID:", "").strip())

    lib.issueBook(book_id)
    messagebox.showinfo("Success", "Book Issued (Added to Queue)")


def return_book():
    book_id = lib.returnBook()

    if book_id == -1:
        messagebox.showerror("Error", "No issued books in queue")
    else:
        messagebox.showinfo("Success", f"Returned Book ID: {book_id}")


# ================= SIDEBAR BUTTONS ================= #

tk.Button(sidebar, text="Add Book", bg="#2196F3",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=add_book).pack(pady=10)

tk.Button(sidebar, text="Delete Book", bg="#E91E63",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=delete_selected).pack(pady=10)

tk.Button(sidebar, text="Undo Delete", bg="#795548",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=undo_delete).pack(pady=10)

tk.Button(sidebar, text="Issue Book", bg="#FF9800",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=issue_book).pack(pady=10)

tk.Button(sidebar, text="Return Book", bg="#9C27B0",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=return_book).pack(pady=10)

tk.Button(sidebar, text="View Books", bg="#009688",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=show_books).pack(pady=10)

tk.Button(sidebar, text="Exit", bg="#f44336",
          fg="white", font=("Arial", 12, "bold"),
          height=2, width=18,
          command=root.quit).pack(pady=20)

# ================= ADD BOOK FORM ================= #

form_frame = tk.LabelFrame(content, text="Add New Book",
                           font=("Arial", 14, "bold"),
                           padx=20, pady=20)
form_frame.pack(fill="x", pady=10)

tk.Label(form_frame, text="Book Name:", font=("Arial", 12)).grid(row=0, column=0, pady=5)
entry_title = tk.Entry(form_frame, width=40)
entry_title.grid(row=0, column=1, pady=5)

tk.Label(form_frame, text="Author:", font=("Arial", 12)).grid(row=1, column=0, pady=5)
entry_author = tk.Entry(form_frame, width=40)
entry_author.grid(row=1, column=1, pady=5)

tk.Label(form_frame, text="Quantity:", font=("Arial", 12)).grid(row=2, column=0, pady=5)
entry_quantity = tk.Entry(form_frame, width=20)
entry_quantity.grid(row=2, column=1, pady=5)

tk.Button(form_frame, text="Submit",
          bg="#2196F3", fg="white",
          font=("Arial", 12, "bold"),
          command=add_book).grid(row=3, columnspan=2, pady=15)

# ================= BOOK LIST TABLE ================= #

table_frame = tk.LabelFrame(content, text="Books List",
                            font=("Arial", 14, "bold"),
                            padx=10, pady=10)
table_frame.pack(fill="both", expand=True)

columns = ("ID", "Title", "Author", "Quantity")

tree = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200)

tree.pack(fill="both", expand=True)

# Load books at startup
show_books()

root.mainloop()
