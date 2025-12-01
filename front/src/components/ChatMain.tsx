import type React from "react";
import "../ChatPage.css";
import type { ChatMessage } from "../types/chat";
interface ChatMainProps {
  messages: ChatMessage[] | undefined;
  userInput: string;
  isSending: boolean;
  handleNewChat: () => void;
  handleSendMessage: (e: React.FormEvent) => void;
  setUserInput: (value: string) => void;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

const ChatMain: React.FC<ChatMainProps> = ({
  messages,
  userInput,
  isSending,
  handleNewChat,
  handleSendMessage,
  setUserInput,
  messagesEndRef,
}) => {
  return (
    <div className="chat-area-wrapper">
      <div className="chat-header">
        <h2>RAG チャット</h2>
        <button onClick={handleNewChat} className="new-chat-button">
          + 新しいチャットを開始
        </button>
      </div>

      {/* 会話メッセージエリア */}
      <div className="messages-area">
        {messages?.length === 0 ? (
          <p className="empty-message">
            質問を入力してチャットを開始してください。
          </p>
        ) : (
          messages?.map((msg) => (
            <div
              key={msg.id}
              className={`message-bubble message-${msg.sender}`}
            >
              <div className="message-text">{msg.text}</div>
              <small className="message-time">
                {msg.timestamp.toLocaleTimeString()}
              </small>
            </div>
          ))
        )}
        {isSending && (
          <div className="loading-message">ボットが回答を生成中です...</div>
        )}
        {/* スクロール位置調整用 */}
        <div ref={messagesEndRef} />
      </div>

      {/* 入力フォーム */}
      <form onSubmit={handleSendMessage} className="input-form">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="ここに質問を入力してください..."
          disabled={isSending}
          className="input-field"
        />
        <button
          type="submit"
          disabled={!userInput.trim() || isSending}
          className="send-button"
        >
          送信
        </button>
      </form>
    </div>
  );
};

export default ChatMain;
