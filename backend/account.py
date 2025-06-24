from datetime import datetime
from mysql.connector import Error
from backend.sql import execQy, fOne, fAll
from backend.constants import LIBRARIAN_HEADERS, MEMBER_HEADERS
from backend.utils import encrypt_password, decrypt_password, validate_fields

HEADERS_MAP = {
    "Librarian": LIBRARIAN_HEADERS,
    "Members": MEMBER_HEADERS,
}

def signup_user(db, email, fullname, password, mobile):
    try:
        if db not in HEADERS_MAP:
            return "Invalid user type."

        if not email or not fullname or not password or not mobile:
            return "All fields are required."

        if not (mobile.isdigit() and len(mobile) == 10):
            return "Invalid mobile number."

        if fOne(f"SELECT 1 FROM {db} WHERE EmailID = %s", (email,)):
            return "Email already registered."

        encrypted_pwd = encrypt_password(password)

        query = f"""
        INSERT INTO {db} (EmailID, FullName, Password, MobileNumber)
        VALUES (%s, %s, %s, %s)
        """
        execQy(query, (email, fullname, encrypted_pwd, mobile))

        return "Signup successful."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def signin_user(db, email, password):
    try:
        if db not in HEADERS_MAP:
            return "Invalid user type."

        if not email or not password:
            return "Email and password are required."

        result = fOne(f"SELECT Password FROM {db} WHERE EmailID = %s", (email,))
        if not result:
            return "Invalid email or password."

        stored_pwd = decrypt_password(result[0])
        if password != stored_pwd:
            return "Invalid email or password."

        execQy(f"UPDATE {db} SET LastLoginOn = %s WHERE EmailID = %s", (datetime.now(), email))
        return "Login successful."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def update_user(db, email, old_password, fullname=None, mobile=None, new_password=None):
    try:
        if db not in HEADERS_MAP:
            return "Invalid user type."

        if not email:
            return "Email is required."
        if not old_password:
            return "Old password is required."

        row = fOne(f"SELECT Password FROM {db} WHERE EmailID = %s", (email,))
        if not row:
            return "Email not found."

        stored_pwd = decrypt_password(row[0])
        if old_password != stored_pwd:
            return "Old password is incorrect."

        fields = []
        values = []

        if fullname:
            fields.append("FullName = %s")
            values.append(fullname)

        if mobile:
            if not (mobile.isdigit() and len(mobile) == 10):
                return "Invalid mobile number."
            fields.append("MobileNumber = %s")
            values.append(mobile)

        if new_password:
            fields.append("Password = %s")
            values.append(encrypt_password(new_password))

        if not fields:
            return "Nothing to update."

        values.append(email)
        query = f"""
        UPDATE {db}
        SET {', '.join(fields)}
        WHERE EmailID = %s
        """
        execQy(query, tuple(values))

        return "Update successful."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def delete_user(db, email, password, librarianEmail=None):
    try:
        if db not in HEADERS_MAP:
            return "Invalid user type."

        if not email or not password:
            return "Email and password are required."

        table = "Members"
        if librarianEmail:
            table = "Librarian"

        row = fOne(f"SELECT Password FROM Librarian WHERE EmailID = %s", (librarianEmail,))
        if not row:
            return "Email not found."

        stored_pwd = decrypt_password(row[0])
        if password != stored_pwd:
            return "Incorrect password."

        execQy(f"DELETE FROM {db} WHERE EmailID = %s", (email,))
        return "Account deleted successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def get_user(db, fields=None, email=None, count=False, bool=False):
    try:
        if db not in HEADERS_MAP:
            return "Invalid user type."
        
        selected_fields = "*"
        if fields:
            selected_fields = validate_fields(fields, HEADERS_MAP[db])
            if selected_fields == "INVALID":
                return "Invalid field(s) provided."

        if email!=None:
            query = f"SELECT {selected_fields} FROM {db} WHERE EmailID = %s"
            row = fOne(query, (email,))
            
            if bool:
                return row is not None  
            return row or f"{db[:-1]} not found."

        if count:
            query = f"SELECT COUNT(*) FROM {db}"
            row = fOne(query)
            return row[0] if row else 0
        
        query = f"SELECT {selected_fields} FROM {db}"
        return fAll(query)

    except Error as e:
        if bool:
            return False
        return f"Database error: {e}"
    except Exception as e:
        if bool:
            return False
        return f"Unexpected error: {e}"
    
def wishlist_mem(email, isbn, action):
    try:
        if not email or not isbn or not action:
            return "Email, ISBN, and action are required."

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN."

        if action not in ("add", "remove"):
            return "Action must be 'add' or 'remove'."

        row = fOne("SELECT WishlistedBooks FROM Members WHERE EmailID = %s", (email,))
        if not row:
            return "Member not found."

        wishlist = row[0].split(",") if row[0] else []

        if action == "add":
            if isbn in wishlist:
                return "ISBN already in wishlist."
            wishlist.append(isbn)

        elif action == "remove":
            if isbn not in wishlist:
                return "ISBN not in wishlist."
            wishlist.remove(isbn)

        updated = ",".join(wishlist)
        execQy("UPDATE Members SET WishlistedBooks = %s WHERE EmailID = %s", (updated, email))
        return f"Wishlist updated successfully ({action})."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def add_points_mem(email, isbn, val=0):
    try:
        if not email or not isbn:
            return "Email and ISBN are required."

        row = fOne("SELECT Genre FROM Books WHERE ISBN = %s", (isbn,))
        if not row:
            return "Book not found."

        genre = row[0]

        points = 10

        row = fOne("SELECT Points FROM Members WHERE EmailID = %s", (email,))
        if not row:
            return "Member not found."

        new_total = row[0] + points
        execQy("UPDATE Members SET Points = %s WHERE EmailID = %s", (new_total, email))
        return points

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def redeem_points_mem(email, points):
    try:
        if not email or not points:
            return "Email and points are required."

        if not points.isdigit() or int(points) <= 0:
            return "Invalid points."

        row = fOne("SELECT Points FROM Members WHERE EmailID = %s", (email,))
        if not row:
            return "Member not found."

        current_points = row[0]
        if current_points < int(points):
            return "Insufficient points."

        new_total = current_points - int(points)
        execQy("UPDATE Members SET Points = %s WHERE EmailID = %s", (new_total, email))
        return f"{points} points redeemed. New total: {new_total}."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"