from mysql.connector import Error
from backend.sql import execQy, fOne,fAll

def add_book_inv(sku, isbn, status, bay, shelf, row, column):
    try:
        if not all([sku, status, isbn, bay, shelf, row, column]):
            return "All fields are required."

        if status not in ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost'):
            return "Invalid status."

        query = """
        INSERT INTO Inventory 
        (SKUNumber, ISBN, Status, BayNumber, ShelfNumber, RowNumber, ColumnNumber)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (sku, isbn, status, bay, shelf, row, column)
        execQy(query, values)

        return "Inventory item added successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

    
def update_book_inv(sku, status=None, 
                    bay=None, shelf=None, row=None, column=None, eraseBInfo=False):
    try:
        if not sku:
            return "SKU is required."

        if not fOne("SELECT * FROM Inventory WHERE SKUNumber = %s", (sku,)):
            return "SKU not found in inventory."

        updates = []
        values = []

        if status:
            allowed = ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost')
            if status not in allowed:
                return "Invalid status."
            updates.append("Status = %s")
            values.append(status)

        if bay is not None:
            updates.append("BayNumber = %s")
            values.append(bay)

        if shelf is not None:
            updates.append("ShelfNumber = %s")
            values.append(shelf)

        if row is not None:
            updates.append("RowNumber = %s")
            values.append(row)

        if column is not None:
            updates.append("ColumnNumber = %s")
            values.append(column)

        if not updates:
            return "No fields provided to update."

        values.append(sku)  

        query = f"""
        UPDATE Inventory
        SET {', '.join(updates)}
        WHERE SKUNumber = %s
        """
        if eraseBInfo == True:
            execQy("UPDATE Inventory SET BayNumber = %s, ShelfNumber = %s, RowNumber = %s, ColumnNumber = %s WHERE SKUNumber = %s",(0,0,0,0, sku))

        execQy(query, tuple(values))
        return "Inventory record updated successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def get_book_inv(isbn=None, sku=None, status=None, count=False):
    try:
        allowed = ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost')
        if status and status not in allowed:
            return "Invalid status."

        sel = "COUNT(*)" if count else "*"
        query = f"SELECT {sel} FROM Inventory"
        conditions, values = [], []

        if isbn:
            if not isbn.isdigit() or len(isbn) not in (10, 13):
                return "Invalid ISBN."
            conditions.append("ISBN = %s")
            values.append(isbn.strip())

        if sku:
            conditions.append("SKUNumber = %s")
            values.append(sku.strip())

        if status:
            conditions.append("Status = %s")
            values.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if count:
            row = fOne(query, tuple(values))
            return row[0] if row else 0

        rows = fAll(query, tuple(values))
        return rows or "No inventory records found."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def delete_book_inv(sku=None, isbn=None, row=None, column=None, shelf=None, bay=None):
    try:
        conditions, values = [], []

        if sku:
            conditions.append("SKUNumber = %s")
            values.append(sku.strip())
        if isbn:
            if not isbn.isdigit() or len(isbn) not in (10, 13):
                return "Invalid ISBN."
            conditions.append("ISBN = %s")
            values.append(isbn.strip())
        if row:
            conditions.append("RowNumber = %s")
            values.append(row)
        if column:
            conditions.append("ColumnNumber = %s")
            values.append(column)
        if shelf:
            conditions.append("ShelfNumber = %s")
            values.append(shelf)
        if bay:
            conditions.append("BayNumber = %s")
            values.append(bay)

        if not conditions:
            return "At least one condition is required to delete inventory items."

        where_clause = " AND ".join(conditions)
        if not fOne(f"SELECT 1 FROM Inventory WHERE {where_clause}", tuple(values)):
            return "No matching inventory items found."

        execQy(f"DELETE FROM Inventory WHERE {where_clause}", tuple(values))
        return "Inventory item(s) deleted successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

