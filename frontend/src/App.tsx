import { ChatInput } from '@/chat/chat-input'
import { useChat } from '@ai-sdk/react';
import { ChatMessage } from './chat/chat-message';
import { cn } from './lib/utils';

import {
  ChatContainerContent,
  ChatContainerRoot,
  ChatContainerScrollAnchor,
} from "@/components/ui/chat-container"
import { ScrollButton } from "@/components/ui/scroll-button"
import { Loader } from './components/ui/loader';

function App() {
  const { messages, input, setInput, status, handleSubmit } = useChat({
    api: "/api/stream",
  });

  return (
    <main className='flex h-screen w-full flex-col justify-center bg-accent'>
      <div
        className={cn(
          messages.length > 0 && "h-[90vh]",
          "max-w-2xl w-full mx-auto px-8 flex flex-col relative transition-all duration-500 ease-in-out"
        )}
      >
        {messages.length > 0 && <div className='flex justify-center mb-8'>
          <h1 className="text-4xl font-elegant font-normal italic">
            Knowmore
          </h1>
        </div>}
        <ChatContainerRoot className={cn(
          (messages.length > 0 || status === "submitted") ? "flex-1 w-full h-full opacity-100" : "hidden opacity-0",
          "scrollbar-hidden transition-opacity duration-500 ease-in-out"
        )}>
          <ChatContainerContent>
            <ChatMessage messages={messages} />
            {status === "submitted" && <Loader variant='typing' />}
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
            "px-6",
            (messages.length > 0 || status == "streaming")
              ? "absolute bottom-0 left-0 right-0 transform translate-y-0 transition-all duration-500 ease-in-out"
              : "transform -translate-y-20"
          )}
        >
          {(messages.length === 0 || status == "streaming") &&
            <div className='flex justify-center mb-8'>
              <h1 className="text-4xl font-elegant font-normal italic">
                Knowmore
              </h1>
            </div>
          }
          <ChatInput input={input} setInput={setInput} status={status} handleSubmit={handleSubmit} />
        </div>
      </div>
    </main >
  )
}

export default App
