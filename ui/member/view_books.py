import ttkbootstrap as ttk
from backend.books import get_book_det
from ui.member.show_details import show_details_page

ACCENT_COLOR = "#6CA6CD"

Books = get_book_det()

def view_books(app, email):
    def show_main_page():
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

        if Books and len(Books) > 0:
            idx = 0
            for book in Books:
                row = idx // 4
                col = idx % 4
                idx += 1

                book_frame = ttk.Frame(scrollable_frame, width=100, height=160, borderwidth=3, bootstyle="dark")
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
                    text=f"{book[2]}\t\t\t\t\t\t\t\t\t\t",
                    font=("Helvetica", 14, "bold"),
                    foreground=ACCENT_COLOR,
                    wraplength=172,
                    anchor="center"
                )
                title_label.pack(padx=5, expand=True, fill="both", anchor="center", side="top")
                title_label.bind("<Button-1>", lambda e, isbn=book[1]: show_details_page(
                    app, email, show_main_page, isbn, write_reviews=True, add_rmv_wiishlist="add"
                ))

                description_label = ttk.Label(
                    book_frame,
                    text=f"Description: {book[3]}",
                    font=("Helvetica", 10),
                    wraplength=200,
                    justify="left"
                )
                description_label.pack(padx=5, expand=True, fill="both")
                description_label.bind("<Button-1>", lambda e, isbn=book[1]: show_details_page(
                    app, email, show_main_page, isbn, write_reviews=True, add_rmv_wiishlist="add"
                ))

                author_label = ttk.Label(
                    book_frame,
                    text=f"Author: {book[4]}",
                    font=("Helvetica", 10)
                )
                author_label.pack(padx=5, expand=True, fill="both")
                author_label.bind("<Button-1>", lambda e, isbn=book[1]: show_details_page(
                    app, email, show_main_page, isbn, write_reviews=True, add_rmv_wiishlist="add"
                ))

                book_frame.bind("<Button-1>", lambda e, isbn=book[1]: show_details_page(
                    app, email, show_main_page, isbn, write_reviews=True, add_rmv_wiishlist="add"
                ))

            for i in range(4):
                scrollable_frame.grid_columnconfigure(i, weight=1)
        else:
            ttk.Label(
                scrollable_frame,
                text="No books found.",
                font=("Helvetica", 14, "bold"),
            ).pack(anchor="w", padx=5)

    show_main_page()
