"use client"

import { Brain, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useSWR from "swr"

export type ModelProvider = "claude" | "openai"

export interface Model {
    id: string
    name: string
    provider: ModelProvider
}

const fetcher = (url: string) => fetch(url).then(res => res.json())

interface ModelSelectorProps {
    selectedModel: string
    onModelChange: (modelId: string) => void
}

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
    const { data, error, isLoading } = useSWR<{ models: Model[] }>('/api/models', fetcher, {
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
    })

    const models = data?.models || []
    const currentModel = models.find(m => m.id === selectedModel) || models[0]

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="size-8 rounded-full" disabled={isLoading || !!error}>
                    <Brain className="size-4 opacity-50" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[200px]">
                <DropdownMenuLabel className="text-xs">
                    {error ? "Error loading models" : "Select Model"}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {error ? (
                    <DropdownMenuItem disabled className="text-sm text-muted-foreground">
                        Failed to load models
                    </DropdownMenuItem>
                ) : isLoading ? (
                    <DropdownMenuItem disabled className="text-sm text-muted-foreground">
                        Loading models...
                    </DropdownMenuItem>
                ) : models.length === 0 ? (
                    <DropdownMenuItem disabled className="text-sm text-muted-foreground">
                        No models available
                    </DropdownMenuItem>
                ) : (
                    models.map(model => (
                        <DropdownMenuItem
                            key={model.id}
                            onSelect={() => onModelChange(model.id)}
                            className="text-sm justify-between cursor-pointer"
                        >
                            {model.name}
                            {currentModel?.id === model.id && <Check className="size-4" />}
                        </DropdownMenuItem>
                    ))
                )}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}