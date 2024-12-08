import React, { useState, useEffect } from 'react';
import './App.css';
import Navbar from './components/Navbar/Navbar';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './views/pages/Home/Home';
import LoginSignup from './components/LoginSignup/login_signup';
import axios from 'axios';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Get stored token from localStorage when the app starts
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      setToken(storedToken);
      setIsLoggedIn(true);  // User is logged in if token exists
    }
  }, []);

  const handleLogout = async () => {
    try {
      if (!token) {
        console.error("Không tìm thấy token.");
        return;
      }

      // Gửi yêu cầu đến backend để đánh dấu peer là không hoạt động khi đăng xuất
      const response = await axios.post('http://127.0.0.1:5000/tracker/peer/set_inactive', {}, {
        headers: {
          Authorization: `Bearer ${token}`,  // Gửi token JWT trong header Authorization
        },
        withCredentials: true,  // Bao gồm thông tin xác thực cho các yêu cầu cross-origin
      });

      // Đăng xuất người dùng ở frontend bằng cách xóa token và cập nhật trạng thái
      setToken(null);
      localStorage.removeItem('access_token'); // Xóa token khỏi localStorage
      setIsLoggedIn(false); // Cập nhật trạng thái đăng nhập thành false

      console.log("Đăng xuất thành công:", response.data);
    } catch (error) {
      // Xử lý lỗi
      console.error("Đăng xuất thất bại:", error?.response?.data?.error || "Không thể đăng xuất.");
    }
};


  return (
    <Router>
      <Navbar isLoggedIn={isLoggedIn} handleLogout={handleLogout} />
      <Routes>
        <Route path="/" element={<Home token={token} />} />
        <Route path="/signin" element={<LoginSignup setIsLoggedIn={setIsLoggedIn} setToken={setToken} />} />
      </Routes>
    </Router>
  );
}

export default App;
