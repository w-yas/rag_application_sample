import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App"; // App はルートコンポーネントとして残す
import { initMsal } from "./auth/msalInstance";

async function startApp() {
  await initMsal();
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

startApp();
