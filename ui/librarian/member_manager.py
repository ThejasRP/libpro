import tkinter as tk
import ttkbootstrap as ttk
from tkinter import StringVar, messagebox
from backend.account import delete_user, get_user, redeem_points_mem, signup_user, update_user

def create_labeled_entry(parent, label, var, show=None):
    ttk.Label(parent, text=label, font=("Century Gothic", 8)).pack(pady=5)
    ttk.Entry(parent, textvariable=var, font=("Century Gothic", 10), show=show).pack(pady=5)

def open_add_member_popup(app, refresh):
    popup = ttk.Toplevel(app)
    popup.geometry("600x400")
    popup.title("Add Member")

    form = ttk.Frame(popup)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="Add New Member", font=("Cambria", 18, "bold")).pack(pady=20)

    name, email, mobile, password = StringVar(), StringVar(), StringVar(), StringVar()
    for label, var in [("Full Name", name), ("Email Address", email), ("Mobile Number", mobile)]:
        create_labeled_entry(form, label, var)
    create_labeled_entry(form, "Password", password, show="*")

    def submit():
        res = signup_user("Members", email.get(), name.get(), password.get(), mobile.get())
        if "Error:" in res:
            messagebox.showerror("Error", res)
        else:
            messagebox.showinfo("Success", "Member added successfully!")
            popup.destroy()
            refresh()

    ttk.Button(form, text="Add Member", command=submit, style="crimson.TButton").pack(pady=10)
    ttk.Label(form, text="Fill the details and click 'Add Member' to create new membership.", font=("Calibri", 10, "italic")).pack(pady=10)

def update_member_popup(app, data, refresh):
    popup = ttk.Toplevel(app)
    popup.geometry("600x400")
    popup.title("Update Member Details")

    form = ttk.Frame(popup)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="Update Member Details", font=("Cambria", 18, "bold")).pack(pady=20)

    name, mobile = StringVar(value=data[1]), StringVar(value=data[4])
    old_pass, new_pass = StringVar(), StringVar()

    for label, var in [("Full Name", name), ("Mobile Number", mobile)]:
        create_labeled_entry(form, label, var)
    create_labeled_entry(form, "Old Password", old_pass, show="*")
    create_labeled_entry(form, "New Password", new_pass, show="*")

    def save():
        res = update_user("Members", data[1], old_pass.get(), name.get(), mobile.get(), new_pass.get())
        if res == "Update successful.":
            messagebox.showinfo("Success", res)
            popup.destroy()
        else:
            messagebox.showerror("Error", res)
        refresh()

    ttk.Button(form, text="Save Changes", command=save, style="crimson.TButton").pack(pady=10)
    ttk.Label(form, text="Enter old password again if you don't want to change it.", font=("Calibri", 10, "italic")).pack(pady=10)

def remove_points_popup(app, refresh):
    selected = table.selection()
    if not selected:
        messagebox.showerror("Error", "No member selected!")
        return

    email = table.item(selected)["values"][1]
    popup = ttk.Toplevel(app)
    popup.geometry("600x400")
    popup.title("Update Pro Points")

    form = ttk.Frame(popup)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="Update Pro Points", font=("Cambria", 18, "bold")).pack(pady=20)

    pointsredeemed = StringVar()

    create_labeled_entry(form, "Enter no. of points redeemed: ", pointsredeemed)

    def save():
        res = redeem_points_mem(email, pointsredeemed.get())
        if "points redeemed" in res:
            messagebox.showinfo("Success", res)
            popup.destroy()
        else:
            messagebox.showerror("Error", res)
        refresh()

    ttk.Button(form, text="Save Changes", command=save, style="crimson.TButton").pack(pady=10)

def open_delete_member_popup(app, table, refresh, admin_email):
    selected = table.selection()
    if not selected:
        messagebox.showerror("Error", "No member selected!")
        return

    email = table.item(selected)["values"][1]

    popup = tk.Toplevel(app)
    popup.geometry("300x150")
    popup.title("Confirm Membership Cancellation")
    popup.grab_set()

    ttk.Label(popup, text=f"Cancel membership for:\n{email}").pack(pady=10)
    ttk.Label(popup, text="Enter Admin Password:").pack()

    password_entry = ttk.Entry(popup, show="*")
    password_entry.pack(pady=5)

    def confirm():
        password = password_entry.get()
        if not password:
            messagebox.showerror("Error", "Password is required.")
            return

        res = delete_user("Members", email, password, admin_email)
        if res == "Account deleted successfully.":
            messagebox.showinfo("Success", "Membership cancelled.")
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Error", res)

    ttk.Button(popup, text="Confirm", command=confirm).pack(pady=10)

def open_update_member_popup(app, refresh):
    selected = table.selection()
    if not selected:
        messagebox.showerror("Error", "No member selected!")
        return

    email = table.item(selected)["values"][1]
    member = get_user("Members", email=email)
    update_member_popup(app, member, refresh)

def populate_table():
    table.delete(*table.get_children())
    for member in get_user("Members"):
        table.insert("", "end", values=(member[0], member[1], member[2], member[4], member[6], member[8]))

def member_manager(app, admin_email):
    global table

    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    frame = ttk.Frame(app)
    frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    columns = ("Member No.", "Email", "Full Name", "Mobile Number", "Points", "Date of Joining")
    table = ttk.Treeview(frame, columns=columns, show="headings", height=40,bootstyle="secondary")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", stretch=True)

    table.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
    table.configure(xscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=0, sticky="ew")

    btn_frame = ttk.Frame(app)
    btn_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    ttk.Button(btn_frame, text="Add New Member", command=lambda: open_add_member_popup(app, populate_table), style="crimson.TButton").pack(fill="x", pady=5)
    ttk.Button(btn_frame, text="Update Member Details", command=lambda: open_update_member_popup(app, populate_table), style="crimson.TButton").pack(fill="x", pady=5)
    ttk.Button(btn_frame, text="Update ProPoints", command=lambda: remove_points_popup(app, populate_table), style="crimson.TButton").pack(fill="x", pady=5)
    ttk.Button(btn_frame, text="Delete Member", command=lambda: open_delete_member_popup(app, table, populate_table, admin_email), style="crimson.TButton").pack(fill="x", pady=5)

    populate_table()
