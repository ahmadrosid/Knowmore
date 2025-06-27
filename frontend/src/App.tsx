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
    api: "/api/stream"
  });

  return (
    <main className='flex h-screen w-full flex-col justify-center bg-accent'>
      <div 
        className={cn(messages.length > 0 && "h-[90vh]", "max-w-2xl w-full mx-auto px-8 flex flex-col relative ")}
      >
        <div className='flex justify-center mb-8'>
          <h1 className="text-4xl font-elegant font-normal italic">
            Knowmore
          </h1>
        </div>
        <div className={cn((messages.length > 0 || status === "submitted") ? "flex-1 w-full h-full max-h-[85vh] pb-32" : "hidden", "scrollbar-hidden overflow-y-auto")}>
          <ChatContainerRoot className="flex-1">
            <ChatContainerContent>
              <ChatMessage messages={messages} />
              {status === "submitted" && <Loader variant='typing' className='my-4'/>}
              <ChatContainerScrollAnchor />
            </ChatContainerContent>
            <div className="absolute left-0 right-0 bottom-4">
              <div className='flex justify-center'>
                <ScrollButton className="shadow-none" />
              </div>
            </div>
          </ChatContainerRoot>
        </div>

        <div className={cn(messages.length > 0 && "absolute bottom-0 left-0 right-0", "px-4")}>
          <ChatInput input={input} setInput={setInput} status={status} handleSubmit={handleSubmit} />
        </div>
      </div>
    </main >
  )
}

export default App
