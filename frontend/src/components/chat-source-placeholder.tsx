import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

export function ChatSourcePlaceholder() {
    return (
        <div className="w-full bg-white backdrop-blur-sm rounded-lg border border-border px-4 pt-2 pb-1">
            {/* Header Section Shimmer */}
            <div className="flex items-center justify-between my-2">
                <div className="h-6 bg-muted rounded animate-pulse w-32" />
                <div className="h-4 bg-muted rounded animate-pulse w-16" />
            </div>

            {/* Filter Tags Shimmer */}
            <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hidden">
                {[...Array(2)].map((_, index) => (
                    <div
                        key={index}
                        className="h-6 bg-muted rounded-full animate-pulse w-16"
                    />
                ))}
            </div>

            {/* Scrollable Results Shimmer */}
            <ScrollArea className="w-full whitespace-nowrap rounded-md">
                <div className="flex w-max space-x-4 mb-3">
                    {[...Array(3)].map((_, index) => (
                        <Card
                            key={index}
                            className="w-[340px] bg-accent border-accent shadow-none py-3"
                        >
                            <CardContent className="p-0">
                                <div className="flex px-2">
                                    {/* Favicon shimmer */}
                                    <div className="flex gap-2">
                                        <div className="flex-shrink-0 w-8 h-8 bg-muted rounded-md animate-pulse" />
                                        <div>
                                            {/* Title shimmer */}
                                            <div className="h-4 bg-muted rounded mb-1 animate-pulse w-40" />
                                            {/* URL shimmer */}
                                            <div className="h-3 bg-muted rounded animate-pulse w-24" />
                                        </div>
                                    </div>
                                </div>

                                {/* Content shimmer */}
                                <div className="flex-1 min-w-0 space-y-2 py-4 px-3">
                                    {/* Preview shimmer */}
                                    <div className="space-y-1">
                                        <div className="h-3 bg-muted rounded animate-pulse w-full" />
                                        <div className="h-3 bg-muted rounded animate-pulse w-3/4" />
                                        <div className="h-3 bg-muted rounded animate-pulse w-1/2" />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </ScrollArea>
        </div>
    );
}
