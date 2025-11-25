import { MsalProvider } from "@azure/msal-react";
import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { msalInstance } from "./auth/msalInstance";
import Home from "./pages/Home";
const App: React.FC = () => {
  return (
    <div>
      <BrowserRouter>
        <MsalProvider instance={msalInstance}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="*" element={<h1>404 Not Found</h1>} />
          </Routes>
        </MsalProvider>
      </BrowserRouter>
    </div>
  );
};

export default App;
