import { loginRequest } from "./msalConfig";
import { msalInstance } from "./msalInstance";

export async function getToken() {
  const account = msalInstance.getActiveAccount();
  if (!account) {
    throw new Error("No active account! Please sign in.");
  }
  try {
    const response = await msalInstance.acquireTokenSilent({
      ...loginRequest,
      account: account,
    });
    return response.accessToken;
  } catch (error) {
    const response = await msalInstance.acquireTokenPopup(loginRequest);
    return response.accessToken;
  }
}
