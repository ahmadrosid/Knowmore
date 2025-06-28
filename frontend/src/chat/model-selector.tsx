"use client"

import { Brain, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuRadioGroup,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export type ModelProvider = "claude" | "openai"

export interface Model {
    id: string
    name: string
    provider: ModelProvider
}

const models: Model[] = [
    { id: "claude-opus-4-20250514", name: "Claude Opus 4", provider: "claude" },
    { id: "claude-sonnet-4-20250514", name: "Claude Sonnet 4", provider: "claude" },
    { id: "claude-3-7-sonnet-20250219", name: "Claude Sonnet 3.7", provider: "claude" },
    { id: "gpt-4o-2024-08-06", name: "GPT-4o", provider: "openai" },
    { id: "o4-mini-2025-04-16", name: "O4 Mini", provider: "openai" },
    { id: "gpt-4.1-2025-04-14", name: "GPT-4.1", provider: "openai" },
]

interface ModelSelectorProps {
    selectedModel: string
    onModelChange: (modelId: string) => void
}

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
    const currentModel = models.find(m => m.id === selectedModel) || models[0]
    return (
        <DropdownMenu >
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="size-8 rounded-full">
                    <Brain className="size-4 opacity-50" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[200px]" >
                <DropdownMenuLabel className="text-xs">Select Model</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuRadioGroup value={selectedModel} onValueChange={onModelChange}>
                    {models.map(model => (
                        <DropdownMenuItem
                            key={model.id}
                            onSelect={() => onModelChange(model.id)}
                            className="text-sm justify-between cursor-pointer"
                        >
                            {model.name}
                            {currentModel.id === model.id &&
                                <Check className="size-4" />}
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuRadioGroup>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}