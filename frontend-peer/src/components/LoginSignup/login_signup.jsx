// LoginSignup.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './login_signup.css';
import user_icon from '../assets/user.png';
import password_icon from '../assets/password.png';

axios.defaults.withCredentials = true;

const LoginSignup = ({ setIsLoggedIn }) => {
  const [action, setAction] = useState("Login");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async () => {
    const url = action === "Login" ? "http://127.0.0.1:5000/peer/login" : "http://127.0.0.1:5000/peer/sign_up";
    try {
      const response = await axios.post(url, { name, password }, { headers: { 'Content-Type': 'application/json' } });
      if (response.status === 201) {
        setMessage(response.data.message);
        if (action === "Login") {
          document.cookie = `peer_id=${response.data.peer_id}; path=/`;
          setIsLoggedIn(true);
          setTimeout(() => {
            navigate('/');
          }, 1000);
        }
      }
    } catch (error) {
      setMessage(error.response ? error.response.data.error || error.response.data.message : "Something went wrong!");
    }
  };

  return (
    <div className='container'>
      <div className='header'>
        <div className='text'>{action}</div>
        <div className='underline'></div>
      </div>
      <div className='inputs'>
        <div className='input'>
          <img src={user_icon} alt="" className='icon' />
          <input type="text" placeholder='Name' value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className='input'>
          <img src={password_icon} alt="" className='icon' />
          <input id="pas" type="password" placeholder='Password' value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
      </div>
      <div className="submit-container">
        <div className={action === "Login" ? "submit gray" : "submit"} onClick={() => setAction("Sign Up")}>Sign Up</div>
        <div className={action === "Sign Up" ? "submit gray" : "submit"} onClick={() => setAction("Login")}>Login</div>
      </div>
      <button onClick={handleSubmit} className='submit choose'>Submit</button>
      {message && <div className="message">{message}</div>}
    </div>
  );
};

export default LoginSignup;
