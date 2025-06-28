"use client"

import {
    Message,
    MessageAction,
    MessageActions,
    MessageContent,
} from "@/components/ui/message"
import { Button } from "@/components/ui/button"
import { Copy, ThumbsDown, ThumbsUp } from "lucide-react"
import { useState, useMemo } from "react"
import { type Message as MessageItem } from "@ai-sdk/react"
import { ChatSource } from "./chat-source"
import { ChatSourcePlaceholder } from "@/components/chat-source-placeholder"
import { Loader } from '@/components/ui/loader';

// Helper function to extract query from tool args
function extractSearchQuery(args: any): string {
    if (typeof args === 'string') {
        try {
            const parsed = JSON.parse(args);
            return parsed.query || '';
        } catch {
            return args;
        }
    }
    return args?.query || '';
}

// Helper function to transform web search results
function transformSearchResults(results: any): any[] {
    if (!Array.isArray(results)) {
        console.warn('transformSearchResults: Expected array but received:', typeof results, results);
        return [];
    }
    
    return results.map((result, index) => ({
        id: `result-${index}`,
        title: result.title || 'Untitled',
        url: result.url || '',
        preview: result.description || result.snippet || 'No preview available',
        favicon: result.url ? new URL(result.url).hostname.charAt(0).toUpperCase() : '?',
        domain: result.url ? new URL(result.url).hostname : 'unknown',
    }));
}

function AssistantMessage({ message }: { message: MessageItem }) {
    const [liked, setLiked] = useState<boolean | null>(null)
    const [copied, setCopied] = useState(false)

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const renderedContent = useMemo(() => {
        if (!message.parts || message.parts.length === 0) {
            return (
                <MessageContent markdown className="bg-transparent p-0">
                    {message.content}
                </MessageContent>
            );
        }

        return message.parts.map((part, partIndex) => {
            switch (part.type) {
                case 'text':
                    return (
                        <MessageContent key={partIndex} markdown className="bg-transparent p-0">
                            {part.text}
                        </MessageContent>
                    );

                case 'tool-invocation': {
                    const invocation = part.toolInvocation as any;
                    const { toolName, state, args } = invocation;

                    if (toolName === 'web_search') {
                        // Show loading state immediately when web_search tool is detected without results
                        if (!invocation.result) {
                            return (
                                <div key={partIndex} className="mb-4">
                                    <ChatSourcePlaceholder />
                                </div>
                            );
                        }
                        
                        if (state === 'result' && invocation.result) {
                            // Transform and display results with additional safety checks
                            const resultsArray = invocation.result?.results || invocation.result || [];
                            const searchResults = transformSearchResults(resultsArray);
                            const query = extractSearchQuery(args);
                            const filterTags = query ? [query] : [];
                            
                            return (
                                <div key={partIndex} className="mb-4">
                                    <ChatSource 
                                        filterTags={filterTags} 
                                        searchResults={searchResults} 
                                    />
                                </div>
                            );
                        }
                    }
                    
                    return null;
                }

                default:
                    return null;
            }
        });
    }, [message.parts, message.content]);

    return (
        <Message className="justify-start px-2">
            <div className="flex w-full flex-col gap-4">
                {renderedContent}

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

export function ChatMessage({ messages, isLoading }: { messages: MessageItem[], isLoading: boolean }) {
    return (
        <div className="flex flex-col gap-8">
            {messages.map((message) => (
                message.role === "user" ? (
                    <Message key={message.id} className="justify-start">
                        <MessageContent>{message.content}</MessageContent>
                    </Message>
                ) : (
                    <AssistantMessage key={message.id} message={message} />
                )
            ))}
            {isLoading && (
                <div>
                    <div className="mb-4">
                        <ChatSourcePlaceholder />
                    </div>
                    <div className="px-4">
                        <Loader variant='typing' />
                    </div>
                </div>
            )}
        </div>
    )
}
