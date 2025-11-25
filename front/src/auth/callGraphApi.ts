import { getToken } from "./getToken";

export async function callGraphApi() {
  const token = await getToken();
  const response = await fetch("https://graph.microsoft.com/v1.0/me", {
    headers: {
      Authorization: `Bearer ${token.accessToken}`,
    },
  });
  return response.json();
}
