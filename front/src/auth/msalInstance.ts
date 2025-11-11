import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "./msalConfig";

// トップレベルで一度だけインスタンス生成
export const msalInstance = new PublicClientApplication(msalConfig);

// msal 3.0.0 以降では initialize メソッドを呼び出す必要がある
export async function initMsal() {
  await msalInstance.initialize();
  console.log("MSAL initialized");
}
