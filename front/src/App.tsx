import React from "react";
import { callGraphApi } from "./auth/callGraphApi";
import { signIn } from "./auth/signIn";

const App: React.FC = () => {
  const [profile, setProfile] = React.useState<any>(null);

  const handleLogin = async () => {
    await signIn();
    const data = await callGraphApi();
    setProfile(data);
  };
  return (
    <div>
      <h1>React MSAL Authentication Example</h1>
      <button onClick={handleLogin}>Sign In and Fetch Profile</button>
      {/* {profile && (
        <div>
          <h2>Profile Information:</h2>
          <pre>{JSON.stringify(profile, null, 2)}</pre>
        </div>
      )} */}
    </div>
  );
};

export default App;
