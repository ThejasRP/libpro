from mysql.connector import Error
from datetime import datetime, timedelta
from backend.account import add_points_mem
from backend.inventory import update_book_inv
from backend.sql import execQy, fAll, fOne

def borrow_book(email, sku, fullname, isbn, daysborrowed):
    try:
        if not all([email, sku, fullname, isbn, daysborrowed]):
            return "All fields are required."

        email, sku, fullname, isbn = map(str.strip, (email, sku, fullname, isbn))
        days = str(daysborrowed).strip()

        if not days.isdigit() or int(days) <= 0:
            return "Days borrowed must be a positive integer."
        days = int(days)

        if fOne("SELECT 1 FROM BooksRecord WHERE SKU = %s AND Status = 'Borrowed'", (sku,)):
            return "This book is already borrowed and not yet returned."

        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn,)):
            return "Invalid ISBN: Book not found."

        due_on = (datetime.now() + timedelta(days=days)).date()
        execQy(
            """
            INSERT INTO BooksRecord 
            (SKU, Status, ISBN, Email, FullName, DaysBorrowed, DueOn)
            VALUES (%s, 'Borrowed', %s, %s, %s, %s, %s)
            """,
            (sku, isbn, email, fullname, days, due_on)
        )
        update_book_inv(sku, status="Borrowed", eraseBInfo=True)
        return "Book borrowed successfully."

    except (Error, Exception) as e:
        return f"Error: {e}"

def return_book(sku):
    try:
        if not sku:
            return "SKU is required."

        record = fOne(
            "SELECT Status, DueOn, Email, ISBN FROM BooksRecord WHERE SKU = %s AND Status = 'Borrowed'",
            (sku,)
        )
        if not record:
            return "Book record not found."

        status, due_on, email, isbn = record

        today = datetime.now().date()
        days_late = max((today - due_on).days, 0)
        fine = round(days_late * 2.0, 2)
        points = 0

        if days_late == 0:
            points = add_points_mem(email, isbn, 1) or 0

        execQy(
            """
            UPDATE BooksRecord
            SET Status = 'Returned',
                ReturnedOn = %s,
                DaysLate = %s,
                Fine = %s,
                Points = %s
            WHERE SKU = %s
            """,
            (today, days_late, fine, points, sku)
        )
        update_book_inv(sku, status="Unshelved")

        return f"Book returned successfully.\n\nFine to be paid: ₹{fine:.2f}/-\nPoints awarded: {points}."

    except (Error, Exception) as e:
        return f"Database error: {e}"

def get_record(sku=None, status=None, email=None, count=False):
    try:
        fields = "COUNT(*)" if count else "*"
        conditions, values = [], []

        if sku:
            conditions.append("SKU = %s")
            values.append(sku)
        if email:
            conditions.append("Email = %s")
            values.append(email)
        if status:
            if status not in ("Borrowed", "Returned", "Lost"):
                return "Invalid status filter."
            conditions.append("Status = %s")
            values.append(status)

        query = f"SELECT {fields} FROM BooksRecord"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if count:
            result = fOne(query, tuple(values))
            return result[0] if result else 0

        if sku and not status:
            result = fOne(query, tuple(values))
            if not result:
                return "No record found for the given SKU."
            keys = [
                "SKU", "Status", "ISBN", "Email", "FullName", "DaysBorrowed", "DueOn",
                "ReturnedOn", "DaysLate", "Fine", "Points", "CreatedOn", "UpdatedOn"
            ]
            record = dict(zip(keys, result))
            record["Fine"] = f"₹{record['Fine']:.2f}/-" if record["Fine"] else "₹0.00/-"
            record["Points"] = record["Points"] or 0
            record["ReturnedOn"] = record["ReturnedOn"] or "Not yet returned"
            record["DaysLate"] = record["DaysLate"] or 0
            return record

        rows = fAll(query, tuple(values))
        return rows or "No records found."

    except (Error, Exception) as e:
        return f"Database error: {e}"

def overdue_books(sku=None, email=None, count=False):
    try:
        today = datetime.now().date()
        values = [today]
        conditions = ["Status = 'Borrowed'", "DueOn < %s"]

        if sku:
            conditions.append("SKU = %s")
            values.append(sku)
        if email:
            conditions.append("Email = %s")
            values.append(email)

        where_clause = " AND ".join(conditions)

        if count:
            query = f"SELECT COUNT(*) FROM BooksRecord WHERE {where_clause}"
            result = fOne(query, tuple(values))
            return result[0] if result else 0

        query = f"""
        SELECT SKU, FullName, DaysLate, DueOn, Fine
        FROM BooksRecord
        WHERE {where_clause}
        """
        records = fAll(query, tuple(values)) or []
        return records or "No overdue records."

    except (Error, Exception) as e:
        return f"Database error: {e}"
