import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

interface SearchResult {
    id: string;
    title: string;
    url: string;
    preview: string;
    favicon: string;
    domain: string;
}

type ChatSourceProps = {
    filterTags: string[];
    searchResults: SearchResult[]
}

export function ChatSource({ filterTags, searchResults }: ChatSourceProps) {
    return (
        <div className="w-full bg-white backdrop-blur-sm rounded-lg border border-border px-4 pt-2 pb-1">
            {/* Header Section */}
            <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold text-foreground">Sources Found</h2>
                <span className="text-sm text-muted-foreground">{searchResults.length} Results</span>
            </div>

            {/* Filter Tags */}
            <div className="flex gap-2 mb-4 overflow-x-auto scrollbar-hidden">
                {filterTags.map((tag, index) => (
                    <Badge
                        key={index}
                        variant="secondary"
                        className="text-secondary-foreground hover:bg-accent border-border"
                    >
                        {tag}
                    </Badge>
                ))}
            </div>

            {/* Scrollable Results */}
            <ScrollArea className="w-full whitespace-nowrap rounded-md">
                <div className="flex w-max space-x-4 mb-3">
                    {searchResults.map((result) => (
                        <Card
                            key={result.id}
                            className="w-[340px] bg-accent shadow-none py-3"
                        >
                            <CardContent className="p-0">
                                <div className="flex px-2">
                                    {/* Favicon */}
                                    <div className="flex gap-2">
                                        <div className="flex-shrink-0 w-8 h-8 bg-white rounded-md flex items-center justify-center text-muted-foreground">
                                            {result.favicon}
                                        </div>
                                        <div>
                                            {/* Title */}
                                            <h3 className="text-sm font-medium text-foreground truncate whitespace-normal line-clamp-1">
                                                {result.title}
                                            </h3>

                                            {/* URL */}
                                            <p className="text-xs text-primary truncate">
                                                {result.domain}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0 space-y-2 py-4 px-3">
                                    {/* Preview */}
                                    <p className="text-xs text-muted-foreground whitespace-normal line-clamp-3">
                                        {result.preview}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
                <ScrollBar orientation="horizontal" />
            </ScrollArea>
        </div>
    );
}