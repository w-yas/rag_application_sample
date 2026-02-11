import type React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import * as ApiTypes from "../api/schema";
import ChatMain from "../components/ChatMain";
import ChatSidebar from "../components/ChatSidebar";
import { client } from "../lib/apiClient";

export type ChatMessage = ApiTypes.components["schemas"]["ChatMessage"];
export type ChatThread = ApiTypes.components["schemas"]["ChatThread"];
type RagChatRequest = ApiTypes.components["schemas"]["RagChatRequest"];
type SearchMode =
  ApiTypes.components["schemas"]["RagChatRequest"]["search_mode"];

const ChatPage: React.FC = () => {
  // message, thread関連
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [isSending, setIsSending] = useState<boolean>(false);
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | undefined>(
    undefined
  );

  useEffect(() => {
    client.GET("/threads").then((response) => {
      if (response.error || !response.data) {
        console.error("Threadsの取得に失敗しました");
      }
      if (response.data.threads && response.data.threads.length > 0) {
        setThreads(response.data.threads);
        setCurrentThreadId(response.data.threads[0]?.id);
      } else {
        client.POST("/thread").then((newThreadResponse) => {
          if (newThreadResponse.error || !newThreadResponse.data) {
            console.error("新しいスレッドの作成に失敗しました");
            return;
          }
          setThreads([newThreadResponse.data as ChatThread]);
          setCurrentThreadId(newThreadResponse.data.id);
        });
      }
    });
  }, []);

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

  useEffect(() => {
    // 現在アクティブなスレッドを見つける
    const activeThread = threads.find((thread) => thread.id == currentThreadId);
    if (activeThread) {
      setMessages(activeThread.messages || []);
    } else {
      setMessages([]);
    }
  }, [threads, currentThreadId]);

  const handleSelectedTopK = useCallback((topK: number) => {
    setTopK(topK);
  }, []);

  const handleSelectedMode = useCallback((mode: SearchMode) => {
    setSearchMode(mode);
  }, []);

  const handleSelectedThread = useCallback((id: string) => {
    setCurrentThreadId(id);
  }, []);

  const handleNewChat = useCallback(async () => {
    const newThread = await client.POST("/thread");
    if (newThread.error || !newThread.data) {
      console.error("Failed to create new thread");
      return;
    }
    console.log("New thread created:", newThread.data);

    // 新しいスレッドをリストの先頭に追加し、それをアクティブにする
    setThreads((prev) => [newThread.data as ChatThread, ...prev]);
    setCurrentThreadId(newThread.data.id);
    setUserInput("");
  }, []);

  const setMessagesInThread = (message: ChatMessage) => {
    if (!currentThreadId) return;

    client.POST("/{thread_id}/message", {
      params: {
        path: {
          thread_id: currentThreadId,
        },
        query: {
          message_text: message.text,
          sender: message.sender,
        },
      },
    });
    setThreads((prevThreads) => {
      return prevThreads.map((thread) => {
        if (thread.id === currentThreadId) {
          return {
            ...thread,
            messages: [...(thread.messages || []), message],
          };
        }
        return thread;
      });
    });
  };

  const updateTitleInThreads = ({
    id,
    newTitle,
  }: {
    id: string;
    newTitle: string;
  }) => {
    setThreads((prevThreads) => {
      return prevThreads.map((thread) => {
        if (thread.id === id) {
          return {
            ...thread,
            title: newTitle,
          };
        }
        return thread;
      });
    });
  };

  const fetchRagResponse = useCallback(
    async (message: string) => {
      setIsSending(true);

      const currentThread = threads.find((t) => t.id == currentThreadId);
      const isFirstMessage =
        currentThread && currentThread.messages?.length === 0;

      if (isFirstMessage && currentThreadId) {
        client.PUT("/thread/{thread_id}/title", {
          params: {
            path: { thread_id: currentThreadId },
            query: {
              new_title:
                message.length > 30
                  ? message.substring(0, 30) + "..."
                  : message,
            },
          },
        });
        updateTitleInThreads({
          id: currentThreadId,
          newTitle:
            message.length > 30 ? message.substring(0, 30) + "..." : message,
        });
      }

      const userMessage: ChatMessage = {
        id: Date.now().toString() + "-user",
        thread_id: currentThreadId || "",
        text: message,
        sender: "user",
        timestamp: new Date().toISOString(),
      };
      console.log("currentThreadId:", currentThreadId);
      setMessagesInThread(userMessage);
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
        if (error) {
          // サーバーからエラーが返ってきた場合 (500 Internal Server Error など)
          console.error("API Error Response:", error);
          const errorMessage: ChatMessage = {
            id: Date.now().toString() + "-error",
            thread_id: currentThreadId || "",
            text: `エラーが発生しました: ${error.detail || "不明なエラー"}`,
            sender: "bot",
            timestamp: new Date().toISOString(),
          };
          setMessagesInThread(errorMessage);
          return;
        }
        const botMessages: ChatMessage = {
          id: Date.now().toString() + "-bot",
          thread_id: currentThreadId || "",
          text: data?.response || "回答を取得できませんでした。",
          sender: "bot",
          timestamp: new Date().toISOString(),
        };
        setMessagesInThread(botMessages);
      } catch (err) {
        console.error("API呼び出し時にネットワークエラーが発生しました:", err);
      } finally {
        setIsSending(false);
      }
    },
    [currentThreadId, topK, searchMode]
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
        currentTopK={topK}
        currentSearchMode={searchMode}
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

import { withAuthRedirect } from "../components/withAuthRedirect";

export default withAuthRedirect(ChatPage);
