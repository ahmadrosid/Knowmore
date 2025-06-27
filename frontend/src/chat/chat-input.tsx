"use client"

import {
  PromptInput,
  PromptInputAction,
  PromptInputActions,
  PromptInputTextarea,
} from "@/components/ui/prompt-input"
import { Button } from "@/components/ui/button"
import { ArrowUp, Square } from "lucide-react"
import { type ChatRequestOptions } from "@ai-sdk/ui-utils";
import { cn } from "@/lib/utils";

interface ChatInputProps {
    input: string;
    status: "submitted" | "streaming" | "ready" | "error";
    setInput: (value: string) => void;
    handleSubmit: (event?: {
        preventDefault?: () => void;
    }, chatRequestOptions?: ChatRequestOptions) => void;   
}

export function ChatInput({ input, setInput, handleSubmit, status }: ChatInputProps) {

  const isLoading = status === "streaming" || status === "submitted";

  return (
    <PromptInput
      value={input}
      onValueChange={(value) => setInput(value)}
      isLoading={isLoading}
      onSubmit={handleSubmit}
      className="w-full max-w-(--breakpoint-md)"
    >
      <PromptInputTextarea placeholder="Ask me anything..." />
      <PromptInputActions className="justify-end pt-2">
        <PromptInputAction
          tooltip={isLoading ? "Stop generation" : "Send message"}
        >
          <Button
            variant="default"
            size="icon"
            className={cn(input.length === 0 && "bg-primary/75" ,"h-8 w-8 rounded-full")}
            onClick={handleSubmit}
          >
            {isLoading ? (
              <Square className="size-3 fill-current" />
            ) : (
              <ArrowUp className="size-4" />
            )}
          </Button>
        </PromptInputAction>
      </PromptInputActions>
    </PromptInput>
  )
}
