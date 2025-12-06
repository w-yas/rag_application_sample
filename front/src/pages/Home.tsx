import type React from "react";
import { Link } from "react-router-dom";

const Home: React.FC = () => {
  return (
    <div>
      <h1>RAG Chatアプリ</h1>
      <p>ようこそ！認証が完了しました。</p>
      <Link to="/chat">チャットを開始する</Link>
    </div>
  );
};

import { withAuthRedirect } from "../components/withAuthRedirect";

export default withAuthRedirect(Home);
