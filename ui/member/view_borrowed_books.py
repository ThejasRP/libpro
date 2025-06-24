import ttkbootstrap as ttk
from tkinter import messagebox
from backend.bookrecord import get_record
from backend.books import get_book_det
from backend.reviews import add_review

def view_borrowed_books(app, email):
    def show_main_page():
        for widget in app.winfo_children():
            widget.destroy()

        brrwd_books = get_record(email=email)
        if not brrwd_books or brrwd_books == "No records found." or brrwd_books[0] == "":
            brrwd_books = []

        main_frame = ttk.Frame(app, padding=30)
        main_frame.pack(fill="both", expand=True)

        main_panel = ttk.Frame(main_frame, padding=20)
        main_panel.pack(side="top", fill="both", expand=True, padx=20, anchor="n")

        canvas = ttk.Canvas(main_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure('hover.TFrame', background='#f0f0f0')

        if brrwd_books:
            for idx, book in enumerate(brrwd_books):
                row, col = divmod(idx, 4)
                book_frame = ttk.Frame(scrollable_frame, width=100, height=160, borderwidth=3, bootstyle="dark")
                book_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                book_frame.grid_propagate(False)

                def on_hover(e, frame=book_frame):
                    frame.configure(style="hover.TFrame")

                def on_leave(e, frame=book_frame):
                    frame.configure(bootstyle="dark")

                book_frame.bind("<Enter>", on_hover)
                book_frame.bind("<Leave>", on_leave)

                b = get_book_det(isbn=book[3])[0]
                ttk.Label(
                    book_frame,
                    text=f"{b[2]}",
                    font=("Helvetica", 14, "bold"),
                    wraplength=172,
                    anchor="center"
                ).pack(padx=5, fill="both", expand=True)

                for txt in [f"{b[3]}", f"{b[4]}"]:
                    ttk.Label(book_frame, text=txt, font=("Helvetica", 10), wraplength=180).pack(padx=5, fill="both")

                for widget in book_frame.winfo_children():
                    widget.bind("<Button-1>", lambda e, sku=book[0]: show_details_page(sku))
                book_frame.bind("<Button-1>", lambda e, sku=book[0]: show_details_page(sku))

            for i in range(4):
                scrollable_frame.grid_columnconfigure(i, weight=1)
        else:
            ttk.Label(
                scrollable_frame,
                text="No books found 📭",
                font=("Helvetica", 14, "bold")
            ).pack(anchor="center", pady=30)

    def show_details_page(sku):
        for widget in app.winfo_children():
            widget.destroy()

        brrwd_books = get_record(email=email)
        book = next((b for b in brrwd_books if b[0] == sku), None)
        if not book:
            messagebox.showerror("Error", "Book not found.")
            show_main_page()
            return

        bd = get_book_det(isbn=book[3])[0]

        container = ttk.Frame(app, padding=20)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="📖 Borrowed Book Details",
            font=("Century Gothic", 18, "bold")
        ).pack(pady=(0, 15), anchor="center") 

        details_frame = ttk.Frame(container, padding=10)
        details_frame.pack(side="left", fill="both", expand=True)


        details = [
            ("SKU", book[1]), ("Status", book[2]), ("ISBN", book[3]), ("Title", bd[2]), ("Author", bd[4]),
            ("Genre", bd[6]), ("Language", bd[7]), ("Borrower", f"{book[5]} ({book[4]})"),
            ("Borrowed On", book[13]), ("Days Borrowed", book[7]), ("Due On", book[10]),
            ("Returned On", book[11] or "Not returned yet"), ("Days Late", book[8]),
            ("Fine (Rs.)", book[9]), ("Points Awarded", book[6]), ("Updated On", book[12])
        ]

        for label, value in details:
            row = ttk.Frame(details_frame, padding=5)
            row.pack(fill="x")
            ttk.Label(row, text=f"{label}:", font=("Helvetica", 13, "bold"), width=15, anchor="w").pack(side="left")
            ttk.Label(row, text=value, font=("Helvetica", 13), anchor="w", wraplength=300).pack(side="left", fill="x", expand=True)

        review_frame = ttk.Frame(container, padding=10)
        review_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(review_frame, text="✍️ Write a Review", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 10))

        review_text = ttk.Text(review_frame, height=6, width=50, wrap="word")
        review_text.pack(fill="x", pady=(0, 10))

        ttk.Label(review_frame, text="⭐ Rating (1 to 5):", font=("Helvetica", 11)).pack(anchor="w", pady=(5, 2))

        rating_var = ttk.StringVar(value="5")
        ttk.Combobox(
            review_frame,
            textvariable=rating_var,
            values=["1", "2", "3", "4", "5"],
            width=5,
            state="readonly"
        ).pack(anchor="w", pady=(0, 10))

        def submit_review():
            review = review_text.get("1.0", "end").strip()
            rating = rating_var.get()
            response = add_review(
                isbn=book[3],
                fullname=book[5],
                email=email,
                review=review,
                rating=rating
            )
            if response == "Review added successfully.":
                messagebox.showinfo("✅ Success", response)
                review_text.delete("1.0", "end")
                rating_var.set("5")
            else:
                messagebox.showerror("❌ Error", response)

        ttk.Button(
            review_frame, text="✅ Submit Review", command=submit_review,
            style="crimson.TButton"
        ).pack(anchor="center", pady=15)

        ttk.Button(
            details_frame, text="🔙 Back", command=show_main_page,
            style="crimson.TButton"
        ).pack(pady=20, anchor="w")

    show_main_page()
