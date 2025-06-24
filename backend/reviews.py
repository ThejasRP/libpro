from mysql.connector import Error
from backend.sql import execQy, fAll, fOne

def add_review(isbn, fullname,email, review, rating):
    try:
        if not isbn or not review or not rating or not fullname or not email:
            return "All fields are required."
        
        if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            return "Rating must be an integer between 1 and 5."

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."

        if not fOne("SELECT * FROM Books WHERE ISBN = %s", (isbn,)):
            return "Book not found."       
        

        query = """
        INSERT INTO Reviews (ISBN, ReviewerName, ReviewerEmail, Rating, Review)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (isbn, fullname, email, rating, review)
        execQy(query, values)

        return "Review added successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def update_review(isbn, email, review, rating):
    try:
        if not isbn or not email or not review or not rating:
            return "All fields are required."
        
        if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            return "Rating must be an integer between 1 and 5."

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."

        if not fOne("SELECT * FROM Books WHERE ISBN = %s", (isbn,)):
            return "Book not found."

        query = """
        UPDATE Reviews
        SET Review = %s, Rating = %s
        WHERE ISBN = %s AND ReviewerEmail = %s
        """
        values = (review, rating, isbn, email)
        execQy(query, values)

        return "Review updated successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def delete_review(isbn, email):
    try:
        if not isbn or not email:
            return "ISBN and email are required."
        
        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."

        if not fOne("SELECT * FROM Books WHERE ISBN = %s", (isbn,)):
            return "Book not found."

        query = """
        DELETE FROM Reviews
        WHERE ISBN = %s AND ReviewerEmail = %s
        """
        values = (isbn, email)
        execQy(query, values)

        return "Review deleted successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def get_reviews(isbn):
    try:
        if not isbn or not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."
        
        reviews = fAll("SELECT * FROM Reviews WHERE ISBN = %s", (isbn,))
        if not reviews:
            return "No reviews found for this book."
        
        return reviews

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"