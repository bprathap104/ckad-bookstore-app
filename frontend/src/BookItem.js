import React from 'react';

function BookItem({ book }) {
  return (
    <div className="book-item">
      <h3>{book.title}</h3>
      <p>by {book.author}</p>
    </div>
  );
}

export default BookItem;
