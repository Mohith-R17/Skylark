import React, { useState } from "react";
import { Mic, MessageCircle, Send, Loader2 } from "lucide-react";
import { LoadingState, EmptyState, } from "@/components/layout";
import { askSkylark } from "@/lib/api";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ExamplePrompt {
  id: string;
  text: string;
}

export default function AskSkylarkPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const handleSend = async (textToSend?: string) => {
    const text = typeof textToSend === 'string' ? textToSend : input;
    if (!text.trim()) return;
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await askSkylark(text);
      
      let finalContent = response.answer;
      if (response.caveats && response.caveats.length > 0) {
        finalContent += "\n\n**Data Notes:**\n" + response.caveats.map((c: string) => `- ${c}`).join("\n");
      }

      const assistantMsg: ChatMessage = {
        id: Date.now().toString() + "1",
        role: "assistant",
        content: finalContent,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: Date.now().toString() + "err",
        role: "assistant",
        content: "Sorry, I encountered an error communicating with the AI service. " + err.message,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const examplePrompts: ExamplePrompt[] = [
    { id: "1", text: "How is our pipeline looking?" },
    { id: "2", text: "Which sectors are performing best?" },
    { id: "3", text: "Which deals need attention?" },
    { id: "4", text: "Compare pipeline with active work orders?" },
  ];

  return (
    <section className="min-h-screen bg-background text-foreground">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold tracking-tight">Ask Skylark</h2>
          <p className="text-muted-foreground text-sm mt-1">
            "Ask questions about pipeline, revenue, sectors, and operations."
          </p>
        </div>

        {/* Example prompts */}
        <div className="grid grid-cols-2 gap-2 mb-6">
          {examplePrompts.map((prompt) => (
            <button
              key={prompt.id}
              className="px-4 py-2 border rounded-lg border-border hover:bg-primary hover:text-primary-foreground transition-colors text-sm"
              onClick={() => setInput(prompt.text)}
            >
              {prompt.text}
            </button>
          ))}
        </div>

        {/* Chat area */}
        <div className="space-y-4 max-h-[500px] overflow-y-auto p-4 rounded-lg bg-muted-foreground/5">
          {messages.length === 0 && (
            <EmptyState
              icon={Mic}
              title="Start a conversation"
              description="Ask me about pipeline, revenue, sectors, or operations"
              actionLabel="Ask a question"
              onAction={() => handleSend("How is our pipeline looking?")}
            />
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end items-end" : "justify-start items-start"}`}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-lg ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground shadow-sm"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start items-start">
              <div className="max-w-[80%] px-4 py-3 rounded-lg bg-card text-foreground shadow-sm flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            </div>
          )}

          {/* Input area with loading state */}
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your question..."
                className="w-full rounded-lg border-border p-3 focus:outline-none focus:border-primary"
                disabled={loading}
              />
            </div>
              <button
                onClick={() => handleSend()}
                className="px-5 py-2 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
                disabled={!input.trim() || loading}
              >
                Send
              </button>
          </div>
        </div>
      </div>
    </section>
  );
}