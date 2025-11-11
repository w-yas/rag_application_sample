import { loginRequest } from "./msalConfig";
import { msalInstance } from "./msalInstance";

export async function signIn() {
  try {
    const loginResponse = await msalInstance.loginPopup(loginRequest);
    console.log("id_token acquired:", loginResponse);
    const account = loginResponse.account;
    if (account) {
      msalInstance.setActiveAccount(account);
    }
  } catch (error) {
    console.error("Login failed:", error);
  }
}
