import type React from "react";
import "../ChatPage.css";
interface HeaderProps {
  userName: string;
}

const Header: React.FC<HeaderProps> = ({ userName }) => {
  return (
    <header className="app-header">
      <h1 className="user-header">RagChat App</h1>
      {userName && <p className="user-name">ようこそ、{userName}さん</p>}
      {!userName && <p className="user-name">ようこそ、未認証のユーザーさん</p>}
    </header>
  );
};

export default Header;
