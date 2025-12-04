import type React from "react";
import * as ApiTypes from "../api/schema";
import "../ChatPage.css";
import type { ChatThread } from "../types/chat";

type SearchMode =
  ApiTypes.components["schemas"]["RagChatRequest"]["search_mode"];

interface ChatSidebarProps {
  threads: ChatThread[];
  currentThreadId: string | undefined;
  onSelectTread: (id: string) => void;
  onNewChat: () => void;
  currentTopK: number;
  currentSearchMode: SearchMode;
  onSelectSearch: (mode: SearchMode) => void;
  onSelectTopK: (topK: number) => void;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  threads,
  currentThreadId,
  onSelectTread,
  onNewChat,
  currentTopK,
  currentSearchMode,
  onSelectSearch,
  onSelectTopK,
}) => {
  const searchModes = ["hybrid", "semantic", "vector"];
  const handleTopKChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value > 0) {
      onSelectTopK(value);
    }
  };
  const handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const mode = e.target.value as SearchMode;
    onSelectSearch(mode);
  };

  return (
    <div className="chat-sidebar">
      <h3 className="sidebar-title">会話履歴</h3>
      <button onClick={onNewChat} className="new-chat-button">
        新しいチャットを開始
      </button>

      <div className="rag-settings">
        <div className="setting-group">
          <label htmlFor="topk-input">Top-K:</label>
          <input
            id="topk-input"
            type="number"
            min="1"
            value={currentTopK}
            onChange={handleTopKChange}
            className="setting-input"
          />
        </div>

        <div className="setting-group">
          <label htmlFor="search-mode-select">検索モード:</label>
          <select
            id="search-mode-select"
            value={currentSearchMode || undefined}
            onChange={handleModeChange}
            className="setting-select"
          >
            {searchModes.map((mode) => (
              <option key={mode} value={mode}>
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="thread-list">
        {threads.map((thread) => (
          <div
            key={thread.id}
            onClick={() => onSelectTread(thread.id)}
            className={`thread-item${
              thread.id === currentThreadId ? " thread-item-active" : ""
            }`}
          >
            <p>{thread.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatSidebar;
