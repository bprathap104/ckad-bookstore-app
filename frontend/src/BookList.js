import React from 'react';
import BookItem from './BookItem';

function BookList({ books }) {
  return (
    <div className="book-list">
      {books.map(book => (
        <BookItem key={book.id} book={book} />
      ))}
    </div>
  );
}

export default BookList;
