import { MsalProvider, useMsal } from "@azure/msal-react";
import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { msalInstance } from "./auth/msalInstance";
import Header from "./components/Header";
import ChatPage from "./pages/ChatPage";
import Home from "./pages/Home";

const App: React.FC = () => {
  return (
    <div>
      <BrowserRouter>
        <MsalProvider instance={msalInstance}>
          <AuthApplayout />
        </MsalProvider>
      </BrowserRouter>
    </div>
  );
};

const AuthApplayout: React.FC = () => {
  const { accounts } = useMsal();
  const userName = accounts[0]?.name || "未認証のユーザー";
  return (
    <>
      <Header userName={userName} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="*" element={<h1>404 Not Found</h1>} />
      </Routes>
    </>
  );
};

export default App;
