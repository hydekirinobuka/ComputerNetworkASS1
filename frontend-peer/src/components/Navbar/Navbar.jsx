import React from 'react';
import { Nav, NavLink, NavMenu, Bar, NavBtn, NavBtnLink } from './NavbarEle';
import logo from '../assets/logoMMT2.png'; 

const Navbar = ({ isLoggedIn, handleLogout }) => {
  return (
    <Nav>
      <NavLink to="/" exact>
        <img src={logo} alt="Logo" style={{ width: "240px", zIndex: 30, position: 'relative' }} />
      </NavLink>
      <Bar />
      <NavMenu>
      </NavMenu>
      {isLoggedIn ? (
        <NavBtn>
          <button onClick={handleLogout} className="nav-btn-logout">
            Log Out
          </button>
        </NavBtn>
      ) : (
        <NavBtn>
          <NavBtnLink to="/signin">Sign In</NavBtnLink>
        </NavBtn>
      )}
    </Nav>
  );
};

export default Navbar;
