import type React from "react";
import "../ChatPage.css";
import type { ChatThread } from "../types/chat";

interface ChatSidebarProps {
  threads: ChatThread[];
  currentThreadId: string | undefined;
  onSelectTread: (id: string) => void;
  onNewChat: () => void;
  onSelectSearch: (mode: string) => void;
  onSelectTopK: (topK: number) => void;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  threads,
  currentThreadId,
  onSelectTread,
  onNewChat,
  onSelectSearch,
  onSelectTopK,
}) => {
  return (
    <div className="chat-sidebar">
      <h3 className="sidebar-title">会話履歴</h3>
      <button onClick={onNewChat} className="new-chat-button">
        新しいチャットを開始
      </button>
      <div className="thread-list">
        {threads.map((thread) => (
          <div
            key={thread.id}
            onClick={() => onSelectTread(thread.id)}
            className={`thread-item${
              thread.id === currentThreadId ? "thread-item-active" : ""
            }`}
          ></div>
        ))}
      </div>
    </div>
  );
};

export default ChatSidebar;
