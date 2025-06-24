import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
from backend.inventory import get_book_inv
from backend.reviews import get_reviews
from backend.books import get_book_det
from backend.account import get_user, wishlist_mem

Books = get_book_det()

def add_to_wishlist(email, isbn):
    res = wishlist_mem(email, isbn, "add")
    if "Error:" in res:
        messagebox.showerror("Error", res)
    else:
        messagebox.showinfo("Wishlist", f"{isbn} added to wishlist successfully!")

def remove_from_wishlist(email, isbn, revert):
    res = wishlist_mem(email, isbn, action="remove")
    if "Error:" in res:
        messagebox.showerror("Error", res)
    else:
        messagebox.showinfo("Wishlist", f"{isbn} removed from wishlist successfully!")
        revert()

def show_details_page(app, email, revert, isbn, write_reviews, add_rmv_wiishlist):
    if add_rmv_wiishlist not in ("add", "remove"):
        print("Invalid wishlist option.")

    for widget in app.winfo_children():
        widget.destroy()

    details_frame = ttk.Frame(app, padding=20)
    details_frame.pack(fill="both", expand=True)

    ttk.Label(details_frame, text="📘 Book Details", font=("Century Gothic", 20, "bold")).pack(pady=(10, 0))
    ttk.Label(details_frame, text="Detailed Information about the selected book.", font=("Arial", 12, "italic")).pack(pady=(0, 10))

    content_frame = ttk.Frame(details_frame)
    content_frame.pack(fill="both", expand=True)

    left_panel = ttk.Frame(content_frame, padding=10)
    left_panel.pack(side="left", fill="both", expand=True)

    left_canvas = ttk.Canvas(left_panel, highlightthickness=0)
    left_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=left_canvas.yview)
    left_scrollable = ttk.Frame(left_canvas)

    left_scrollable.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
    left_canvas.create_window((0, 0), window=left_scrollable, anchor="nw")
    left_canvas.configure(yscrollcommand=left_scroll.set)

    left_canvas.pack(side="left", fill="both", expand=True)
    left_scroll.pack(side="right", fill="y")

    book = next((b for b in Books if b[1] == isbn), None)
    if not book:
        messagebox.showerror("Error", "Book not found.")
        revert()
        return

    details = [
        ("ISBN", book[1]),
        ("Title", book[2]),
        ("Description", book[3]),
        ("Author", book[4]),
        ("Publication", book[5]),
        ("Genre", book[6]),
        ("Language", book[7]),
        ("Added On", book[8]),
        ("Updated On", book[9]),
    ]

    for label, value in details:
        f = ttk.Frame(left_scrollable, padding=5)
        f.pack(fill="x", anchor="w")
        ttk.Label(f, text=f"{label}:", font=("Helvetica", 13, "bold")).pack(anchor="w")
        ttk.Label(f, text=value, font=("Helvetica", 13), wraplength=350).pack(anchor="w")

    qty = get_book_inv(isbn=isbn, count=True)
    ttk.Label(
        left_scrollable,
        text=f"Quantity: {qty if qty > 0 else 'All copies have been borrowed.'}",
        font=("Helvetica", 13, "bold"),
    ).pack(anchor="w", pady=10)

    right_panel = ttk.Frame(content_frame, padding=20)
    right_panel.pack(side="right", fill="both", expand=True)

    if write_reviews:
        ttk.Label(right_panel, text="✍️ Write a Review", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 10))

        review_input = ttk.Text(right_panel, height=5, wrap="word")
        review_input.pack(fill="x", pady=(0, 10))

        ttk.Label(right_panel, text="Rating (1-5):", font=("Helvetica", 11)).pack(anchor="w")
        rating_var = ttk.StringVar(value="5")
        ttk.Combobox(right_panel, textvariable=rating_var, values=["1", "2", "3", "4", "5"], width=5, state="readonly").pack(anchor="w", pady=(0, 10))

        def submit_review():
            from backend.reviews import add_review
            review = review_input.get("1.0", "end").strip()
            rating = rating_var.get()
            fullname = get_user("Members", email=email, fields=["FullName"])[0]

            result = add_review(isbn=book[1], fullname=fullname, email=email, review=review, rating=rating)
            if "successfully" in result:
                messagebox.showinfo("Success", result)
                show_details_page(app, email, revert, isbn, write_reviews, add_rmv_wiishlist)  # refresh UI
            else:
                messagebox.showerror("Error", result)


        ttk.Button(right_panel, text="Submit", command=submit_review, style="crimson.TButton").pack(anchor="center", pady=5)

    ttk.Label(right_panel, text="🗨️ All Reviews", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(20, 5))

    review_canvas = ttk.Canvas(right_panel, highlightthickness=0)
    review_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=review_canvas.yview)
    review_scrollable = ttk.Frame(review_canvas)

    review_scrollable.bind("<Configure>", lambda e: review_canvas.configure(scrollregion=review_canvas.bbox("all")))
    review_canvas.create_window((0, 0), window=review_scrollable, anchor="nw")
    review_canvas.configure(yscrollcommand=review_scroll.set)

    review_canvas.pack(side="left", fill="both", expand=True)
    review_scroll.pack(side="right", fill="y")

    reviews = get_reviews(isbn)
    if reviews != "No reviews found for this book.":
        for review in reviews:
            reviewer, rating, content = review[2], review[4], review[5]
            ttk.Label(review_scrollable, text=f"👤 {reviewer}", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(5, 0), padx=5)
            ttk.Label(review_scrollable, text=f"⭐ Rating: {rating}/5", font=("Helvetica", 10)).pack(anchor="w", padx=5)
            ttk.Label(review_scrollable, text=content, font=("Helvetica", 10), wraplength=350).pack(anchor="w", padx=5)
            ttk.Label(review_scrollable, text="─" * 40).pack(pady=5)
    else:
        ttk.Label(review_scrollable, text="No reviews yet!", font=("Helvetica", 11)).pack(anchor="w", padx=5)

    footer = ttk.Frame(details_frame, padding=10)
    footer.pack(side="bottom", fill="x")

    if add_rmv_wiishlist == "add":
        ttk.Button(footer, text="➕ Add to Wishlist", command=lambda: add_to_wishlist(email, isbn), style="crimson.TButton").pack(side="left", padx=5)
    elif add_rmv_wiishlist == "remove":
        ttk.Button(footer, text="❌ Remove from Wishlist", command=lambda: remove_from_wishlist(email, isbn, revert), style="crimson.TButton").pack(side="left", padx=5)

    ttk.Button(footer, text="⬅ Back", command=revert, style="crimson.TButton").pack(side="right", padx=5)
