// src/App.jsx
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from "./pages/Home"
import Navigation from "./components/Navigation"
import React, {useEffect, useState} from 'react';
import { Loader2 } from 'lucide-react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {

  const [isLoggedIn, setIsLoggedIn] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);
  
  useEffect(() => {

    if(isLoggedIn) {
      setIsLoading(false);
      return
    }

    const checkLogin = async () => {
      const tokenData = JSON.parse(localStorage.getItem('tokenInfo'));
      if(!tokenData) {
        setIsLoading(false);
        console.log("No token data found");
        localStorage.removeItem('tokenInfo');
        localStorage.removeItem('userInfo');
        return;
      }

      const userResponse = await fetch('http://localhost:8000/api/auth/user-data', {
        headers: {
          'Authorization': `Bearer ${tokenData.access_token}`,
          'Accept': 'application/json'
        }
      });
      console.log(userResponse)
      if (!userResponse.ok) {
        setIsLoading(false);
        console.log("No User data found");
        localStorage.removeItem('tokenInfo');
        localStorage.removeItem('userInfo');
        return;
      }

      const userData = await userResponse.json();
      console.log(userData)
      console.log("Login Status: ", true);
      setIsLoggedIn(true);
      setIsLoading(false);
    }

    checkLogin();
  }, []);

  return (
    <Router>
      <ToastContainer
        position="bottom-left"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
      <div className="min-h-screen bg-gray-100">
        <Navigation isLoggedIn = {isLoggedIn} setIsLoggedIn = {setIsLoggedIn} setIsLoading={setIsLoading}/>
        {
          isLoading ? (
            <div className="min-h-screen flex items-center justify-center">
              <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
            </div>
          ):
          <Routes>
            <Route path="/" element={<Home/>} />
          </Routes>
        }
      </div>
    </Router>
  );
}

export default App;