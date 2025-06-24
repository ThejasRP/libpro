from mysql.connector import Error
from backend.sql import execQy, fAll, fOne
from backend.inventory import delete_book_inv

def add_book_det(isbn, title, author, publication, genre, language, description=None):
    try:
        if not isbn or not title or not author or not publication or not genre or not language:
            return "All fields except description are required."

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."

        query = """
        INSERT INTO Books (ISBN, Title, Description, Author, Publication, Genre, Language)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (isbn, title, description, author, publication, genre, language)
        execQy(query, values)

        return "Book added successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def update_book_det(isbn, title=None, description=None, author=None, publication=None, genre=None, language=None, review=None):
    try:
        if not isbn:
            return "ISBN is required."

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."

        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn,)):
            return "Book not found."

        fields = []
        values = []

        if title:
            fields.append("Title = %s")
            values.append(title)

        if description:
            fields.append("Description = %s")
            values.append(description)

        if author:
            fields.append("Author = %s")
            values.append(author)

        if publication:
            fields.append("Publication = %s")
            values.append(publication)

        if genre:
            fields.append("Genre = %s")
            values.append(genre)

        if language:
            fields.append("Language = %s")
            values.append(language)

        if review:
            fields.append("Review = %s")
            values.append(review)

        if not fields:
            return "Nothing to update."

        values.append(isbn)
        query = f"""
        UPDATE Books
        SET {', '.join(fields)}
        WHERE ISBN = %s
        """
        execQy(query, tuple(values))
        return "Book updated successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def delete_book_det(isbn):
    try:
        if not isbn:
            return "ISBN is required."

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Invalid ISBN. Must be 10 or 13 digits."

        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn,)):
            return "Book not found."

        query = "DELETE FROM Books WHERE ISBN = %s"
        execQy(query, (isbn,))
        delete_book_inv(isbn=isbn) 

        return "Book deleted successfully."

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def get_book_det(isbn=None, title=None, author=None, publication=None, genre=None, language=None):
    try:
        if not isbn and not title and not author and not publication and not genre and not language:
            rows = fAll("SELECT * FROM Books")
            if not rows:
                return "No books found."
            return rows

        if isbn and (not isbn.isdigit() or len(isbn) not in (10, 13)):
            return "Invalid ISBN. Must be 10 or 13 digits."

        query = "SELECT * FROM Books WHERE "
        conditions = []
        values = []

        if isbn:
            conditions.append("ISBN = %s")
            values.append(isbn)

        if title:
            conditions.append("Title LIKE %s")
            values.append(f"%{title}%")

        if author:
            conditions.append("Author LIKE %s")
            values.append(f"%{author}%")

        if publication:
            conditions.append("Publication LIKE %s")
            values.append(f"%{publication}%")

        if genre:
            conditions.append("Genre LIKE %s")
            values.append(f"%{genre}%")

        if language:
            conditions.append("Language LIKE %s")
            values.append(f"%{language}%")

        query += " AND ".join(conditions)
        rows = fAll(query, tuple(values))

        return rows

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def get_books_list(isbns):
    try:
        if not isbns:
            return "ISBNs are required."

        for isbn in isbns:
            if not (isbn.isdigit() and len(isbn) in (10, 13)):
                return "Invalid ISBNs. Must be 10 or 13 digits."

        placeholders = ','.join(['%s'] * len(isbns))
        query = f"SELECT * FROM Books WHERE ISBN IN ({placeholders})"
        rows = fAll(query, tuple(isbns))

        if not rows:
            return "No books found."

        return rows

    except Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"