import tkinter as tk
from tkinter import StringVar, ttk, messagebox
from backend.inventory import add_book_inv, get_book_inv, update_book_inv

def show_deshelved_books():
    books = get_book_inv(status="Unshelved")
    if isinstance(books, str): 
        messagebox.showerror("Error", books)
        return

    if not books:
        messagebox.showinfo("Deshelved Books", "No books have been deshelved.")
        return

    books_list = "\n".join([f"SKU: {book[0]}" for book in books])
    messagebox.showinfo("Deshelved Books", f"Deshelved Books:\n\n{books_list}")

def open_shelve_popup(app, update_shelf_view):
    def shelve_book():
        try:
            sku = sku_entry.get()
            isbn = isbn_entry.get()
            bay = int(bay_entry.get())
            shelf = int(shelf_entry.get())
            row = int(row_entry.get())
            column = int(column_entry.get())

            if not sku:
                raise ValueError("SKU cannot be empty.")

            result = add_book_inv(sku, isbn, "Shelved", bay, shelf, row, column)
            messagebox.showinfo("Success", result)

            update_shelf_view()
            popup.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    popup = tk.Toplevel(app)
    popup.title("Shelve Book")

    sku_var = StringVar()

    tk.Label(popup, text="SKU").grid(row=0, column=0, padx=10, pady=5)
    sku_entry = tk.Entry(popup, textvariable=sku_var)
    sku_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(popup, text="ISBN").grid(row=1, column=0, padx=10, pady=5)
    isbn_entry = tk.Entry(popup)
    isbn_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(popup, text="Bay Number").grid(row=2, column=0, padx=10, pady=5)
    bay_entry = tk.Entry(popup)
    bay_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(popup, text="Shelf Number").grid(row=3, column=0, padx=10, pady=5)
    shelf_entry = tk.Entry(popup)
    shelf_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(popup, text="Row Number").grid(row=4, column=0, padx=10, pady=5)
    row_entry = tk.Entry(popup)
    row_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(popup, text="Column Number").grid(row=5, column=0, padx=10, pady=5)
    column_entry = tk.Entry(popup)
    column_entry.grid(row=5, column=1, padx=10, pady=5)


    ttk.Button(popup, text="Submit", command=shelve_book, style="crimson.TButton").grid(row=6, column=0, columnspan=2, pady=20)

def open_update_popup(app, update_shelf_view):
    def shelve_book():
        try:
            sku = sku_entry.get()
            status = status_entry.get()
            bay = int(bay_entry.get())
            shelf = int(shelf_entry.get())
            row = int(row_entry.get())
            column = int(column_entry.get())

            if not sku:
                raise ValueError("SKU cannot be empty.")

            result = update_book_inv(sku=sku, status=status, bay=bay, shelf=shelf, row=row, column=column)
            messagebox.showinfo("Success", result)

            update_shelf_view()
            popup.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    popup = tk.Toplevel(app)
    popup.title("Shelve Book")

    sku_var = StringVar()

    tk.Label(popup, text="SKU").grid(row=0, column=0, padx=10, pady=5)
    sku_entry = tk.Entry(popup, textvariable=sku_var)
    sku_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(popup, text="Status").grid(row=1, column=0, padx=10, pady=5)
    status_entry = tk.Entry(popup)
    status_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(popup, text="Bay Number").grid(row=2, column=0, padx=10, pady=5)
    bay_entry = tk.Entry(popup)
    bay_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(popup, text="Shelf Number").grid(row=3, column=0, padx=10, pady=5)
    shelf_entry = tk.Entry(popup)
    shelf_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(popup, text="Row Number").grid(row=4, column=0, padx=10, pady=5)
    row_entry = tk.Entry(popup)
    row_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(popup, text="Column Number").grid(row=5, column=0, padx=10, pady=5)
    column_entry = tk.Entry(popup)
    column_entry.grid(row=5, column=1, padx=10, pady=5)


    ttk.Button(popup, text="Submit", command=shelve_book, style="crimson.TButton").grid(row=6, column=0, columnspan=2, pady=20)


def bay_manager(app):
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    paned_window = ttk.PanedWindow(app, orient="horizontal")
    paned_window.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    outer_canvas = tk.Canvas(paned_window, bg="#1e1e1e", highlightthickness=0)
    paned_window.add(outer_canvas, weight=4)

    outer_scroll = ttk.Scrollbar(app, orient=tk.HORIZONTAL, command=outer_canvas.xview, bootstyle="dark")
    outer_canvas.configure(xscrollcommand=outer_scroll.set)
    outer_scroll.grid(row=1, column=0, sticky="ew")

    outer_frame = tk.Frame(outer_canvas, bg="#1e1e1e")
    outer_frame_id = outer_canvas.create_window((0, 0), window=outer_frame, anchor="nw")

    def resize_outer_frame(event):
        outer_canvas.itemconfig(outer_frame_id, height=event.height)

    outer_canvas.bind("<Configure>", resize_outer_frame)

    right_frame = ttk.Frame(paned_window, width=200)
    paned_window.add(right_frame, weight=1)

    ttk.Button(right_frame, text="Add New Book to Inventory", command=lambda: open_shelve_popup(app, update_shelf_view), style="crimson.TButton").grid(row=0, column=0, pady=10)
    ttk.Button(right_frame, text="Re-add Book / Update Book Position", command=lambda: open_update_popup(app, update_shelf_view), style="crimson.TButton").grid(row=1, column=0, pady=10)
    ttk.Button(right_frame, text="View Deshelved Books", command=lambda: show_deshelved_books(), style="crimson.TButton").grid(row=4, column=0, pady=10)

    def update_shelf_view():
        for widget in outer_frame.winfo_children():
            widget.destroy()

        books = get_book_inv()
        bay_map = {}
        for book in books:
            bay_no, shelf_no, row, col = book[3], book[4], book[5], book[6]
            if bay_no == 0 or shelf_no == 0 or row == 0 or col == 0:
                continue 
            bay_map.setdefault(bay_no, []).append(book)

        for bay_index, bay_books in sorted(bay_map.items()):
            bay_scroll_frame = tk.Frame(outer_frame, bg="#1e1e1e")
            bay_scroll_frame.pack(side=tk.LEFT, padx=30, fill=tk.Y, expand=True)

            bay_canvas = tk.Canvas(bay_scroll_frame, width=280, height=500, bg="#1e1e1e", highlightthickness=0)
            bay_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

            bay_v_scroll = ttk.Scrollbar(bay_scroll_frame, orient=tk.VERTICAL, command=bay_canvas.yview, bootstyle="dark")
            bay_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            bay_canvas.configure(yscrollcommand=bay_v_scroll.set)

            bay_frame = tk.Frame(bay_canvas, bg="white", width=280)
            bay_canvas.create_window((0, 0), window=bay_frame, anchor="nw")

            tk.Label(bay_frame, text=f"Bay {bay_index}", font=("Arial", 12, "bold"), bg="white").pack(pady=5)

            shelf_map = {}
            shelf_indices = set()
            for book in bay_books:
                shelf_index = book[4]  
                shelf_map.setdefault(shelf_index, []).append(book)
                shelf_indices.add(shelf_index)

            for shelf_index in sorted(shelf_indices):
                shelf_books = shelf_map.get(shelf_index, [])
                shelf_canvas_frame = tk.Frame(bay_frame, bg="#e0e0e0", height=220, bd=1, relief="solid", highlightbackground="#cccccc", highlightthickness=1)
                shelf_canvas_frame.pack(fill=tk.X, pady=10)

                label = tk.Label(shelf_canvas_frame, text=f"Shelf {shelf_index}", font=("Arial", 9, "bold"), bg="#e0e0e0", anchor="w")
                label.pack(fill=tk.X)

                shelf_canvas = tk.Canvas(shelf_canvas_frame, width=240, height=180, bg="#e0e0e0", highlightthickness=0)
                shelf_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

                row_height, col_width = 30, 60
                padding = 10

                if shelf_books:
                    for book in shelf_books:
                        row, col = book[5], book[6]
                        x0 = col * col_width + padding
                        y0 = row * row_height + padding
                        x1 = x0 + col_width
                        y1 = y0 + row_height
                        shelf_canvas.create_rectangle(x0, y0, x1, y1, fill="lightgreen", outline="black")
                        shelf_canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=book[0], font=("Arial", 8), width=col_width - 4)
                else:
                    shelf_canvas.create_text(120, 90, text="No books", font=("Arial", 10, "italic"), fill="gray")
                shelf_canvas.config(scrollregion=shelf_canvas.bbox("all"))

            bay_frame.update_idletasks()
            bay_canvas.config(scrollregion=bay_canvas.bbox("all"))

            def on_enter(event, canvas=bay_canvas):
                canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

            def on_leave(event, canvas=bay_canvas):
                canvas.unbind_all("<MouseWheel>")

            bay_canvas.bind("<Enter>", on_enter)
            bay_canvas.bind("<Leave>", on_leave)

        outer_frame.update_idletasks()
        outer_canvas.config(scrollregion=outer_canvas.bbox("all"))

    update_shelf_view()
