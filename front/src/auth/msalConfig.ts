import type { Configuration } from "@azure/msal-browser";
import { BrowserCacheLocation, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${
      import.meta.env.VITE_TENANT_ID
    }`,
    knownAuthorities: [],
    redirectUri: import.meta.env.VITE_REDIRECT_URI,
    postLogoutRedirectUri: import.meta.env.VITE_POST_LOGOUT_REDIRECT_URI,
    navigateToLoginRequestUrl: false, // ログイン後に元のURLにリダイレクトするかどうか
  },
  cache: {
    cacheLocation: BrowserCacheLocation.SessionStorage, // セッションストレージを使用
  },
  system: {
    loggerOptions: {
      loggerCallback: (
        level: LogLevel,
        message: string,
        containsPii: boolean
      ): void => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            return;
          case LogLevel.Info:
            console.info(message);
            return;
          case LogLevel.Verbose:
            console.debug(message);
            return;
          case LogLevel.Warning:
            console.warn(message);
            return;
        }
      },
      piiLoggingEnabled: true, // PII（個人識別情報）をログに含める
    },
    windowHashTimeout: 60000,
    iframeHashTimeout: 6000,
    loadFrameTimeout: 0,
    asyncPopups: false,
  },
  telemetry: {
    application: {
      appName: "react-msal-auth",
      appVersion: "1.0.0",
    },
  },
};

export const loginRequest = {
  scopes: ["openid", "profile", "User.Read"],
};
