import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Auth from "./pages/Auth";
import BookAmbulance from "./pages/BookAmbulance";
import Status from "./pages/Status";

function App() {
  const [user, setUser] = useState(null);

  if (!user) {
    return <Auth setUser={setUser} />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<BookAmbulance user={user} />} />
        <Route path="/status" element={<Status user={user} />} />
      </Routes>
    </Router>
  );
}

export default App;
