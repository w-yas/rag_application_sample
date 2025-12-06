import {
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
  useMsal,
} from "@azure/msal-react";
import React from "react";
import { loginRequest } from "../auth/msalConfig";

export const withAuthRedirect = (Commponent: React.FC) => {
  const WrappedComponent: React.FC = (props) => {
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
      <>
        <AuthenticatedTemplate>
          <Commponent {...props} />
        </AuthenticatedTemplate>
        <UnauthenticatedTemplate>
          <p>サインインする必要があります。</p>
          <button onClick={() => handleLogin()}>
            Microsoft アカウントでサインイン
          </button>
        </UnauthenticatedTemplate>
      </>
    );
  };
  return WrappedComponent;
};
