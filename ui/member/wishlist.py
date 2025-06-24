import ttkbootstrap as ttk
from backend.books import get_book_det
from backend.account import get_user
from ui.member.show_details import show_details_page

def wishlist(app, email,db):

    def show_main_page():
        Books = []
        wishlisted_books = get_user(db=db, email=email, fields=["WishlistedBooks"])
        for book in wishlisted_books:
                Books = book.split(",")
        if wishlisted_books == "No records found." or Books[0] == "": Books = []

        for widget in app.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(app, padding=30)
        main_frame.pack(fill="both", expand=True)

        main_panel = ttk.Frame(main_frame, padding=20)
        main_panel.pack(side="top", fill="both", expand=True, padx=20, anchor="n")

        canvas = ttk.Canvas(main_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure('hover.TFrame', background='#f0f0f0', borderwidth=0)
        
        if len(Books)>0:
            idx = 0
            for book in Books:
                row = idx // 4
                col = idx % 4
                idx = idx + 1
                book_frame = ttk.Frame(scrollable_frame, width=100, height=160,borderwidth=3, bootstyle="dark")
                book_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                book_frame.grid_propagate(False)  

                def on_hover(e, frame=book_frame):
                    frame.configure(style="hover.TFrame")

                def on_leave(e, frame=book_frame):
                    frame.configure(bootstyle="dark")

                book_frame.bind("<Enter>", on_hover)
                book_frame.bind("<Leave>", on_leave)
                title_label = ttk.Label(
                    book_frame,
                    text=f"{get_book_det(isbn=book)[0][2]}\t\t\t\t\t\t\t\t\t\t",
                    font=("Helvetica", 14, "bold"),
                    style="crimson.TButton",
                    wraplength=172,
                    anchor="center"
                )
                title_label.pack(padx=5, expand=True, fill="both", anchor="center", side="top")
                title_label.bind("<Button-1>", lambda e, isbn=book: show_details_page(app, email, show_main_page(), isbn, write_reviews=False, add_rmv_wiishlist="remove"))

                description_label = ttk.Label(
                    book_frame,
                    text=f"Description: {get_book_det(isbn=book)[0][3]}",
                    font=("Helvetica", 10),
                    wraplength=200, 
                    justify="left"
                )
                description_label.pack(padx=5, expand=True, fill="both")
                description_label.bind("<Button-1>", lambda e, isbn=book: show_details_page(app, email, show_main_page(), isbn, write_reviews=False, add_rmv_wiishlist="remove"))

                author_label = ttk.Label(
                    book_frame,
                    text=f"Author: {get_book_det(isbn=book)[0][4]}",
                    font=("Helvetica", 10)
                )
                author_label.pack(padx=5, expand=True, fill="both")
                author_label.bind("<Button-1>", lambda e, isbn=book: show_details_page(app, email, show_main_page(), isbn, write_reviews=False, add_rmv_wiishlist="remove"))

                book_frame.bind("<Button-1>", lambda e, isbn=book: show_details_page(app, email, show_main_page(), isbn, write_reviews=False, add_rmv_wiishlist="remove"))

            for i in range(4):
                scrollable_frame.grid_columnconfigure(i, weight=1)

        else:
            ttk.Label(
                scrollable_frame,
                text="No books found.",
                font=("Helvetica", 14, "bold"),
            ).pack(anchor="w", padx=5)

    show_main_page()