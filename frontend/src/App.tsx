import { cn } from '@/lib/utils';
import { ChatInput } from '@/chat/chat-input'
import { useChat } from '@ai-sdk/react';
import { ChatMessage } from '@/chat/chat-message';
import { ChatHeader } from '@/chat/chat-header';
import {
  ChatContainerContent,
  ChatContainerRoot,
  ChatContainerScrollAnchor,
} from "@/components/ui/chat-container"
import { ScrollButton } from "@/components/ui/scroll-button"
import { useState } from 'react';

export default function App() {
  const [selectedModel, setSelectedModel] = useState(() => {
    const stored = localStorage.getItem('selectedModel');
    return stored || "claude-3-5-sonnet-latest";
  });
  
  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    localStorage.setItem('selectedModel', modelId);
  };
  
  const { messages, input, setInput, status, handleSubmit } = useChat({
    api: "/api/stream",
    body: {
      model: selectedModel,
      enable_web_search: true,
    },
    maxSteps: 5, // Enable multi-step for tool calls
  });

  return (
    <main className='flex h-screen w-full flex-col justify-center bg-accent'>
      <div
        className={cn(
          messages.length > 0 && "h-[95vh]",
          "max-w-3xl w-full mx-auto px-12 flex flex-col relative transition-all duration-500 ease-in-out"
        )}
      >
        {messages.length > 0 && <ChatHeader />}
        <ChatContainerRoot className={cn(
          (messages.length > 0 || status === "submitted") ? "flex-1 w-full" : "hidden",
          "scrollbar-hidden transition-opacity duration-500 ease-in-out"
        )}>
          <ChatContainerContent className={messages.length > 0 ? "mb-32" : ""}>
            <ChatMessage messages={messages} isLoading={status === "submitted"} />
            <ChatContainerScrollAnchor />
          </ChatContainerContent>
          <div className="absolute bottom-4 left-0 right-0 pb-20 pointer-events-none">
            <div className='flex justify-center py-4'>
              <ScrollButton className="shadow-none pointer-events-auto" />
            </div>
          </div>
        </ChatContainerRoot>
        <div
          className={cn(
            "px-12",
            messages.length > 0
              ? "absolute bottom-0 left-0 right-0 transform translate-y-0 transition-all duration-500 delay-300 ease-in-out"
              : "transform -translate-y-20"
          )}
        >
          {messages.length === 0 && <ChatHeader />}
          <ChatInput 
            input={input} 
            setInput={setInput} 
            status={status} 
            handleSubmit={handleSubmit}
            selectedModel={selectedModel}
            onModelChange={handleModelChange}
          />
        </div>
      </div>
    </main >
  )
}
