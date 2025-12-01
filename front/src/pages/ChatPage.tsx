import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import * as ApiTypes from "../api/schema";
import ChatMain from "../components/ChatMain";
import ChatSidebar from "../components/ChatSidebar";
import { client } from "../lib/apiClient";
import type { ChatMessage, ChatThread } from "../types/chat";

type RagChatRequest = ApiTypes.components["schemas"]["RagChatRequest"];
type SearchMode =
  ApiTypes.components["schemas"]["RagChatRequest"]["search_mode"];

const initialThreads: ChatThread[] = [
  {
    id: `${Date.now()}`,
    title: "最初の会話",
    messages: [],
  },
];

const ChatPage: React.FC = () => {
  // message, thread関連
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [isSending, setIsSending] = useState<boolean>(false);
  const [threads, setThreads] = useState<ChatThread[]>(initialThreads);
  const [currentThreadId, setCurrentThreadId] = useState<string | undefined>(
    initialThreads[0]?.id
  );

  // Search関連
  const [topK, setTopK] = useState<number>(3);
  const [searchMode, setSearchMode] = useState<SearchMode>("hybrid");

  // スクロールを一番下にするための Ref
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // メッセージ追加時にスクロール
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  const handleSelectedTopK = useCallback((topK: number) => {
    setTopK(topK);
  }, []);

  const handleSelectedMode = useCallback((mode: SearchMode) => {
    setSearchMode(mode);
  }, []);

  const handleSelectedThread = useCallback((id: string) => {
    setCurrentThreadId(id);
  }, []);

  const handleNewChat = useCallback(() => {
    const newThread: ChatThread = {
      id: `${Date.now()}`,
      title: "新規チャット",
      messages: [],
    };
    // 新しいスレッドをリストの先頭に追加し、それをアクティブにする
    setThreads((prev) => [newThread, ...prev]);
    setCurrentThreadId(newThread.id);
  }, []);

  const setMessagesInThread = (Message: ChatMessage) => {
    setThreads((prevThreads) => {
      return prevThreads.map((thread) => {
        // 現在のスレッドIDと一致する場合
        if (thread.id === currentThreadId) {
          return {
            ...thread,
            messages: [...thread.messages, Message],
          };
        }
        return thread;
      });
    });
  };

  const fetchRagResponse = useCallback(
    async (message: string) => {
      setIsSending(true);

      const userMessage: ChatMessage = {
        id: Date.now().toString + "-user",
        text: message,
        sender: "user",
        timestamp: new Date(),
      };
      setMessagesInThread(userMessage);
      setMessages((prevMessages) => [...prevMessages, userMessage]);

      try {
        const requestBody: RagChatRequest = {
          query: message,
          top_k: topK,
          search_mode: searchMode,
          model: "gpt-4o",
        };
        const { data, error } = await client.POST("/chat", {
          body: requestBody,
        });
        if (error || !data) {
          console.error("API Error");
          throw new Error(
            `API call failed: ${JSON.stringify(error || "No data")}`
          );
        }

        const botMessages: ChatMessage = {
          id: Date.now().toString() + "-bot",
          text: data.response,
          sender: "bot",
          timestamp: new Date(),
        };
        setMessages((prevMessages) => [...prevMessages, botMessages]);
        setMessagesInThread(botMessages);
      } catch (error) {
        console.error("Error during RAG API call:", error);
        const errorMessage: ChatMessage = {
          id: Date.now().toString() + "-error",
          text: "エラーが発生しました。システム管理者にお問い合わせください",
          sender: "bot",
          timestamp: new Date(),
        };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
        setMessagesInThread(errorMessage);
        setIsSending(false);
      }
    },
    [currentThreadId]
  );

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || isSending) return;

    const messageToSend = userInput;
    setUserInput(""); // 入力フィールドをクリア
    fetchRagResponse(messageToSend);
  };
  return (
    <div className="chat-container">
      <ChatSidebar
        threads={threads}
        currentThreadId={currentThreadId}
        onSelectTread={handleSelectedThread}
        onNewChat={handleNewChat}
        onSelectSearch={handleSelectedMode}
        onSelectTopK={handleSelectedTopK}
      />
      <ChatMain
        messages={messages}
        userInput={userInput}
        isSending={isSending}
        handleNewChat={handleNewChat}
        handleSendMessage={handleSendMessage}
        setUserInput={setUserInput}
        messagesEndRef={messagesEndRef}
      />
    </div>
  );
};

export default ChatPage;
