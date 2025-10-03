import React, { useState, useEffect } from 'react';
import Header from './Header';
import Search from './Search';
import BookList from './BookList';
import './App.css';

function App() {
  const [books, setBooks] = useState([]);
  const [filteredBooks, setFilteredBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/books')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch books');
        }
        return response.json();
      })
      .then(data => {
        setBooks(data);
        setFilteredBooks(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching books:', error);
        setError(error.message);
        setLoading(false);
      });
  }, []);

  const handleSearch = (query) => {
    const filtered = books.filter(book =>
      book.title.toLowerCase().includes(query.toLowerCase()) ||
      book.author.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredBooks(filtered);
  };

  if (loading) {
    return (
      <div className="app">
        <Header />
        <p>Loading books...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <Header />
        <p>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Header />
      <Search onSearch={handleSearch} />
      <h2>Available Books</h2>
      <BookList books={filteredBooks} />
    </div>
  );
}

export default App;
