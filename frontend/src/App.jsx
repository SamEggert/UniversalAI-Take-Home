import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import DocumentUpload from './DocumentUpload';
import Autocomplete from './Autocomplete';
import './App.css';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        {/* Fixed Navigation Bar */}
        <nav className="fixed top-0 left-0 w-full bg-white shadow-md z-10">
          <div className="flex justify-center p-4">
            <Link to="/chat" className="mx-4 text-lg text-gray-800 hover:underline">
              Chat
            </Link>
            <Link to="/upload" className="mx-4 text-lg text-gray-800 hover:underline">
              Upload Documents
            </Link>
          </div>
        </nav>

        {/* Main Content */}
        <div className="flex-1 mt-16">
          <Routes>
            <Route
              path="/chat"
              element={
                <div className="center-container">
                  <Autocomplete />
                </div>
              }
            />
            <Route
              path="/upload"
              element={
                <div className="center-container">
                  <DocumentUpload />
                </div>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
