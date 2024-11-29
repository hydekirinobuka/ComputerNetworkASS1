import styled from 'styled-components';
import { NavLink as Link } from 'react-router-dom'; 
import { FaBars } from 'react-icons/fa';

export const Nav = styled.nav`
    background: #fff;
    height: 92px;
    display: flex;
    justify-content: space-between;
    border-bottom: 2px solid #09B814;
    background: #fff;
    background: rgba(255, 255, 255, 0.9);
    padding: 0.5rem calc((100vw - 1500px) / 2);
    z-index: 10;
    position: relative;
`;

export const NavLink = styled(Link)`
    color: #fff;
    display: flex;
    align-items: center;
    text-decoration: none;
    padding: 0 1rem;
    height: 100%;
    cursor: pointer;
    position: relative; 
    z-index: 20; 
    img {
        position: relative;
        z-index: 30; 
    }
    &.active {
        color: #15cdfc;
    }

`

export const Bar = styled(FaBars)`
    display: none;
    color: #fff;
    @media screen and (max-width: 768px) {
        display: block;
        position: absolute;
        top: 0;
        right: 0;
        transform: translate(-100%, 75%);
        font-size: 1.8rem;
        cursor: pointer;
    }

`  


export const NavMenu = styled.div`
    display: flex;
    align-items: center;
    margin-right: -24px;
    
    @media screen and (max-width: 768px) {
        display: none;
    }
    
`

export const NavBtn = styled.nav`
    display: flex;
    align-items: center;
    margin-right: 24px;
    
    @media screen and (max-width: 768px) {
        display: none;
    }

.nav-btn-logout {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #09B814;
    width: 150px;
    height: 50px;
    color: white;
    font-size:24px;
    font-weight: bold;
    padding: 10px 20px;
    border:none;
    border-radius: 15px;
    text-decoration: none; /* Loại bỏ dấu gạch chân */
    transition: background-color 0.3s ease;
}

.nav-btn-logout:hover {
  background-color: #3cc3f0;
}

`;


export const NavBtnLink = styled(Link)`
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #09B814;
  width: 150px;
  height: 50px;
  color: white;
  font-size:24px;
  font-weight: bold;
  padding: 10px 20px;
  border-radius: 25px;
  text-decoration: none; /* Loại bỏ dấu gạch chân */
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #3cc3f0;
  }
`;


