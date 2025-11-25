import React from "react";
import type { components } from "../api/schema";
import { callGraphApi } from "../auth/callGraphApi";
import { signIn } from "../auth/signIn";
import { client } from "../lib/apiClient";

type RagChatRequest = components["schemas"]["RagChatRequest"];
type RagChatResponse = components["schemas"]["RagChatResponse"];

const Home: React.FC = () => {
  const [profile, setProfile] = React.useState<any>(null);
  const [apiResult, setApiResult] = React.useState<any>(null);
  const [searchResult, setSearchResult] = React.useState<any>(null);

  const sample: RagChatRequest = {
    query: "sample",
    top_k: 3,
    search_mode: "full",
    model: "gpt-4o",
  };

  const handleLogin = async () => {
    await signIn();
    const data = await callGraphApi();
    setProfile(data);
  };
  const handleCallRoot = async () => {
    const response = await client.GET("/");
    setApiResult(response.data);
  };
  const handleSearch = async () => {
    const response = await client.POST("/chat", {
      body: {
        query: "sample",
        top_k: 3,
        search_mode: "full",
        model: "gpt-4o",
      },
    });
    setSearchResult(response);
  };
  return (
    <div>
      <h1>React MSAL Authentication Example</h1>
      <div>
        <button onClick={handleLogin}>Sign In and Fetch Profile</button>
      </div>
      <div>
        <button onClick={handleCallRoot}>Call API</button>
      </div>
      <div>
        <button onClick={handleSearch}> Call Search with Auth</button>
      </div>
      <h2>Profile</h2>
      <pre>{profile ? JSON.stringify(profile, null, 2) : "No profile"}</pre>

      <h2>API Result (/)</h2>
      <pre>{apiResult ? JSON.stringify(apiResult, null, 2) : "Noresult"}</pre>
    </div>
  );
};

export default Home;
