// Home.tsx
import {
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
  useMsal,
} from "@azure/msal-react";
import type React from "react";
import { Link } from "react-router-dom";
import { loginRequest } from "../auth/msalConfig";

const Home: React.FC = () => {
  const { instance } = useMsal();

  const handleLogin = async () => {
    try {
      const loginResponse = await instance.loginPopup(loginRequest);

      console.log("id_token acquired:", loginResponse);
      const account = loginResponse.account;

      if (account) {
        instance.setActiveAccount(account);
      }
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <div>
      <h1>RAG Chatアプリ</h1>
      <AuthenticatedTemplate>
        <p>ようこそ！認証が完了しました。</p>
        <Link to="/chat">チャットを開始する</Link>
      </AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <p>サインインしてチャットを始める必要があります。</p>
        <button onClick={() => handleLogin()}>
          Microsoft アカウントでサインイン
        </button>
      </UnauthenticatedTemplate>
    </div>
  );
};

export default Home;
