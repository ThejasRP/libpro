from mysql.connector import Error
from backend.account import add_points_mem
from backend.inventory import update_book_inv
from backend.sql import execQy, fAll, fOne
from datetime import datetime, timedelta

def borrow_book(email, sku, fullname, isbn, daysborrowed):
    try:
        if not email or not sku or not fullname or not isbn or daysborrowed is None:
            return "All fields are required."

        email = str(email).strip()
        sku = str(sku).strip()
        fullname = str(fullname).strip()
        isbn = str(isbn).strip()
        days = str(daysborrowed).strip()

        if not days.isdigit() or int(days) <= 0:
            return "Days borrowed must be a positive integer."
        days = int(days)

        if fOne("SELECT * FROM BooksRecord WHERE SKU = %s AND Status = 'Borrowed'", (sku,)):
            return "This book is already borrowed and not yet returned."

        if not fOne("SELECT * FROM Books WHERE ISBN = %s", (isbn,)):
            return "Invalid ISBN: Book not found."

        due_on = (datetime.now() + timedelta(days=days)).date()

        query = """
        INSERT INTO BooksRecord 
        (SKU, Status, ISBN, Email, FullName, DaysBorrowed, DueOn)
        VALUES (%s, 'Borrowed', %s, %s, %s, %s, %s)
        """
        values = (sku, isbn, email, fullname, days, due_on)
        execQy(query, values)
        update_book_inv(sku, status="Borrowed", eraseBInfo = True)

        return "Book borrowed successfully."

    except Error as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def return_book(sku):
    try:
        if not sku:
            return "SKU is required."

        record = fOne("SELECT Status, DueOn, Email, ISBN FROM BooksRecord WHERE SKU = %s AND Status = 'Borrowed'", (sku,))
        if not record:
            return "Book record not found."

        status, due_on, email, isbn = record

        if status != "Borrowed":
            return "Book is not currently marked as borrowed."

        today = datetime.now().date()
        days_late = max((today - due_on).days, 0)
        fine = round(days_late * 2.0, 2)
        points = 0

        if days_late == 0:
            points = add_points_mem(email, isbn, 1) or 0 

        query = """
        UPDATE BooksRecord
        SET Status = 'Returned',
            ReturnedOn = %s,
            DaysLate = %s,
            Fine = %s,
            Points = %s
        WHERE SKU = %s
        """
        values = (today, days_late, fine, points, sku)
        execQy(query, values)
        update_book_inv(sku, status="Unshelved")
        print("fefe")
        return f"Book returned successfully.\n\nFine to be paid: ₹{fine:.2f}/-\nPoints awarded: {points}."

    except Error as e:
        print(e)
        return f"Database error: {e}"
    except Exception as e:
        print(e)
        return f"Unexpected error: {e}"
    
def get_record(sku=None, status=None, email=None, count=False):
    try:
        sel = "COUNT(*)" if count else "*"
        q = f"SELECT {sel} FROM BooksRecord"
        cond, vals = [], []
        if sku:
            cond.append("SKU = %s"); vals.append(sku)
        if email:
            cond.append("Email = %s"); vals.append(email)
        if status:
            if status not in ("Borrowed", "Returned", "Lost"):
                return "Invalid status filter."
            cond.append("Status = %s"); vals.append(status)
        if cond:
            q += " WHERE " + " AND ".join(cond)
        if count:
            r = fOne(q, tuple(vals))
            return r[0] if r else 0
        if sku and not status:
            r = fOne(q, tuple(vals))
            if not r:
                return "No record found for the given SKU."
            fields = ["SKU", "Status", "ISBN", "Email", "FullName", "DaysBorrowed", "DueOn", "ReturnedOn", "DaysLate", "Fine", "Points", "CreatedOn", "UpdatedOn"]
            res = dict(zip(fields, r))
            res["Fine"] = f"₹{res['Fine']:.2f}/-" if res["Fine"] else "₹0.00/-"
            res["Points"] = res["Points"] or 0
            res["ReturnedOn"] = res["ReturnedOn"] or "Not yet returned"
            res["DaysLate"] = res["DaysLate"] or 0
            return res
        rows = fAll(q, tuple(vals))
        return rows or "No records found."
    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def overdue_books(sku=None, email=None, count=False):
    try:
        today = datetime.now().date()
        vals = [today]
        cond = ["Status = 'Borrowed'", "DueOn < %s"]
        if sku:
            cond.append("SKU = %s");     
            vals.append(sku)
        if email:
            cond.append("Email = %s");   
            vals.append(email)
        where = " AND ".join(cond)
        if count:
            q = f"SELECT COUNT(*) FROM BooksRecord WHERE {where}"
            r = fOne(q, tuple(vals))
            return r[0] if r else 0

        q = f"SELECT SKU, FullName, DaysLate ,DueOn, Fine FROM BooksRecord WHERE {where}"
        rows = fAll(q, tuple(vals)) or []
        result = []
        for s, name, days, due, fine in rows:
            result.append((s, name, days, due, fine))
        return result or "No overdue records."
    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

