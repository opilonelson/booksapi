from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Use environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://flaskuser:secret@localhost/flaskapi")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model: Book
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author, "isbn": self.isbn}

with app.app_context():
    db.create_all()

# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author') or not data.get('isbn'):
        return jsonify({"error": "Title, author, and ISBN are required"}), 400

    book = Book(title=data['title'], author=data['author'], isbn=data['isbn'])
    db.session.add(book)

    try:
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "ISBN must be unique"}), 400

# Get all books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books])

# Get a single book
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

# Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        book.isbn = data['isbn']

    try:
        db.session.commit()
        return jsonify(book.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "ISBN must be unique"}), 400

# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
