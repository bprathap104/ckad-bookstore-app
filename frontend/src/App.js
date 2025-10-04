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
  const [reportLogs, setReportLogs] = useState('');
  const [reportLoading, setReportLoading] = useState(false);

  useEffect(() => {
    fetch('/books')
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

  const handleTriggerReport = () => {
    setReportLoading(true);
    setReportLogs('');
    fetch('/trigger-report', { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        setReportLoading(false);
        if (data.logs) {
          setReportLogs(data.logs);
          console.log('Sales Report Logs:', data.logs);
        } else {
          setReportLogs(`Error: ${data.error}`);
          console.error('Error:', data.error);
        }
      })
      .catch(error => {
        setReportLoading(false);
        setReportLogs(`Error: ${error.message}`);
        console.error('Error triggering report:', error);
      });
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
      <button onClick={handleTriggerReport} disabled={reportLoading} style={{ margin: '10px', padding: '8px 16px' }}>
        {reportLoading ? 'Generating Report...' : 'Trigger Sales Report'}
      </button>
      {reportLogs && (
        <div style={{ margin: '10px', padding: '10px', border: '1px solid #ccc', backgroundColor: '#f9f9f9' }}>
          <h3>Sales Report Logs:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>{reportLogs}</pre>
        </div>
      )}
      <Search onSearch={handleSearch} />
      <h2>Available Books</h2>
      <BookList books={filteredBooks} />
    </div>
  );
}

export default App;
