"use client"

import {
    Message,
    MessageAction,
    MessageActions,
    MessageContent,
} from "@/components/ui/message"
import { Button } from "@/components/ui/button"
import { Copy, ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"
import { type Message as MessageItem } from "@ai-sdk/react"

function AssistantMessage({ message }: { message: MessageItem }) {
    const [liked, setLiked] = useState<boolean | null>(null)
    const [copied, setCopied] = useState(false)

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <Message key={message.id} className="justify-start">
            <div className="flex w-full flex-col gap-2">
                <MessageContent markdown className="bg-transparent p-0">
                    {message.content}
                </MessageContent>

                <MessageActions className="self-start">
                    <MessageAction tooltip="Copy to clipboard">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 rounded-full"
                            onClick={() => handleCopy(message.content)}
                        >
                            <Copy className={`size-4 ${copied ? "text-green-500" : ""}`} />
                        </Button>
                    </MessageAction>

                    <MessageAction tooltip="Helpful">
                        <Button
                            variant="ghost"
                            size="icon"
                            className={`h-8 w-8 rounded-full ${liked === true ? "bg-green-100 text-green-500" : ""}`}
                            onClick={() => setLiked(true)}
                        >
                            <ThumbsUp className="size-4" />
                        </Button>
                    </MessageAction>

                    <MessageAction tooltip="Not helpful">
                        <Button
                            variant="ghost"
                            size="icon"
                            className={`h-8 w-8 rounded-full ${liked === false ? "bg-red-100 text-red-500" : ""}`}
                            onClick={() => setLiked(false)}
                        >
                            <ThumbsDown className="size-4" />
                        </Button>
                    </MessageAction>
                </MessageActions>
            </div>
        </Message>
    );
}

export function ChatMessage({ messages }: { messages: MessageItem[] }) {

    return (
        <div className="flex flex-col gap-8">
            {messages.map((message) => (
                message.role === "user" ? (
                    <Message key={message.id} className="justify-end">
                        <MessageContent>{message.content}</MessageContent>
                    </Message>
                ) : (
                    <AssistantMessage message={message} />
                )
            ))}
        </div>
    )
}
