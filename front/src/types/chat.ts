export type ChatMessage = {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  documents?: string[];
};

export type ChatThread = {
  id: string;
  title: string;
  messages: ChatMessage[];
};
