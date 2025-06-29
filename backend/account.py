from datetime import datetime
from mysql.connector import Error
from backend.sql import execQy, fOne, fAll
from backend.constants import LIBRARIAN_HEADERS, MEMBER_HEADERS
from backend.utils import encrypt_password, decrypt_password, validate_fields

HEADERS_MAP = {
    "Librarian": LIBRARIAN_HEADERS,
    "Members": MEMBER_HEADERS,
}

def _validate_user_type(db):
    if db not in HEADERS_MAP:
        raise ValueError("Invalid user type.")

def _validate_mobile(mobile):
    if not (mobile and mobile.isdigit() and len(mobile) == 10):
        raise ValueError("Invalid mobile number.")

def _get_password_from_db(db, email):
    row = fOne(f"SELECT Password FROM {db} WHERE EmailID = %s", (email,))
    if not row:
        raise ValueError("Email not found.")
    return decrypt_password(row[0])

def signup_user(db, email, fullname, password, mobile):
    try:
        _validate_user_type(db)

        if not all([email, fullname, password, mobile]):
            return "All fields are required."
        
        _validate_mobile(mobile)

        if fOne(f"SELECT 1 FROM {db} WHERE EmailID = %s", (email,)):
            return "Email already registered."

        execQy(
            f"INSERT INTO {db} (EmailID, FullName, Password, MobileNumber) VALUES (%s, %s, %s, %s)",
            (email, fullname, encrypt_password(password), mobile),
        )
        return "Signup successful."

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"

def signin_user(db, email, password):
    try:
        _validate_user_type(db)
        if not email or not password:
            return "Email and password are required."

        stored_pwd = _get_password_from_db(db, email)
        if password != stored_pwd:
            return "Invalid email or password."

        execQy(f"UPDATE {db} SET LastLoginOn = %s WHERE EmailID = %s", (datetime.now(), email))
        return "Login successful."

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"

def update_user(db, email, old_password, fullname=None, mobile=None, new_password=None):
    try:
        _validate_user_type(db)
        if not email or not old_password:
            return "Email and old password are required."

        stored_pwd = _get_password_from_db(db, email)
        if old_password != stored_pwd:
            return "Old password is incorrect."

        fields, values = [], []

        if fullname:
            fields.append("FullName = %s")
            values.append(fullname)
        if mobile:
            _validate_mobile(mobile)
            fields.append("MobileNumber = %s")
            values.append(mobile)
        if new_password:
            fields.append("Password = %s")
            values.append(encrypt_password(new_password))

        if not fields:
            return "Nothing to update."

        values.append(email)
        execQy(f"UPDATE {db} SET {', '.join(fields)} WHERE EmailID = %s", tuple(values))
        return "Update successful."

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"

def delete_user(db, email, password, librarianEmail=None):
    try:
        _validate_user_type(db)
        if not email or not password:
            return "Email and password are required."

        row = fOne("SELECT Password FROM Librarian WHERE EmailID = %s", (librarianEmail,))
        if not row:
            return "Email not found."

        if decrypt_password(row[0]) != password:
            return "Incorrect password."

        execQy(f"DELETE FROM {db} WHERE EmailID = %s", (email,))
        return "Account deleted successfully."

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"

def get_user(db, fields=None, email=None, count=False, bool=False):
    try:
        _validate_user_type(db)

        selected_fields = validate_fields(fields, HEADERS_MAP[db]) if fields else "*"
        if selected_fields == "INVALID":
            return "Invalid field(s) provided."

        if email:
            row = fOne(f"SELECT {selected_fields} FROM {db} WHERE EmailID = %s", (email,))
            return (row is not None if bool else row or f"{db[:-1]} not found.")

        if count:
            row = fOne(f"SELECT COUNT(*) FROM {db}")
            return row[0] if row else 0

        return fAll(f"SELECT {selected_fields} FROM {db}")

    except (ValueError, Error) as e:
        return False if bool else str(e)
    except Exception as e:
        return False if bool else f"Unexpected error: {e}"

def wishlist_mem(email, isbn, action):
    try:
        if not email or not isbn or not action:
            return "Email, ISBN, and action are required."
        if not (isbn.isdigit() and len(isbn) in (10, 13)):
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
        else:  # remove
            if isbn not in wishlist:
                return "ISBN not in wishlist."
            wishlist.remove(isbn)

        execQy("UPDATE Members SET WishlistedBooks = %s WHERE EmailID = %s", (",".join(wishlist), email))
        return f"Wishlist updated successfully ({action})."

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"

def add_points_mem(email, isbn, val=0):
    try:
        if not email or not isbn:
            return "Email and ISBN are required."

        if not fOne("SELECT Genre FROM Books WHERE ISBN = %s", (isbn,)):
            return "Book not found."

        row = fOne("SELECT Points FROM Members WHERE EmailID = %s", (email,))
        if not row:
            return "Member not found."

        new_total = row[0] + 10
        execQy("UPDATE Members SET Points = %s WHERE EmailID = %s", (new_total, email))
        return 10

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"

def redeem_points_mem(email, points):
    try:
        if not email or not points:
            return "Email and points are required."
        if not str(points).isdigit() or int(points) <= 0:
            return "Invalid points."

        row = fOne("SELECT Points FROM Members WHERE EmailID = %s", (email,))
        if not row:
            return "Member not found."

        current_points = row[0]
        points = int(points)
        if current_points < points:
            return "Insufficient points."

        new_total = current_points - points
        execQy("UPDATE Members SET Points = %s WHERE EmailID = %s", (new_total, email))
        return f"{points} points redeemed. New total: {new_total}."

    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {e}"
