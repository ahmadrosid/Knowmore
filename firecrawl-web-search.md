# Firecrawl Search | Firecrawl

Firecrawl’s search API allows you to perform web searches and optionally scrape the search results in one operation.

- Choose specific output formats (markdown, HTML, links, screenshots)
- Search the web with customizable parameters (location, etc.)
- Optionally retrieve content from search results in various formats
- Control the number of results and set timeouts

For details, see the [Search Endpoint API Reference](https://docs.firecrawl.dev/api-reference/endpoint/search).

### /search endpoint

Used to perform web searches and optionally retrieve content from the results.

### Installation

```
pip install firecrawl-py
```

### Basic Usage

```
curl -X POST https://api.firecrawl.dev/v1/search \

  -H "Content-Type: application/json" \

  -H "Authorization: Bearer fc-YOUR_API_KEY" \

  -d '{

    "query": "firecrawl web scraping",

    "limit": 5

  }'
```

### Response

SDKs will return the data object directly. cURL will return the complete payload.

```
{

  "success": true,

  "data": [

    {

      "title": "Firecrawl - The Ultimate Web Scraping API",

      "description": "Firecrawl is a powerful web scraping API that turns any website into clean, structured data for AI and analysis.",

      "url": "https://firecrawl.dev/"

    },

    {

      "title": "Web Scraping with Firecrawl - A Complete Guide",

      "description": "Learn how to use Firecrawl to extract data from websites effortlessly.",

      "url": "https://firecrawl.dev/guides/web-scraping/"

    },

    {

      "title": "Firecrawl Documentation - Getting Started",

      "description": "Official documentation for the Firecrawl web scraping API.",

      "url": "https://docs.firecrawl.dev/"

    }

    // ... more results

  ]

}
```

## Search with Content Scraping

Search and retrieve content from the search results in one operation.

```
curl -X POST https://api.firecrawl.dev/v1/search \

  -H "Content-Type: application/json" \

  -H "Authorization: Bearer fc-YOUR_API_KEY" \

  -d '{

    "query": "firecrawl web scraping",

    "limit": 3,

    "scrapeOptions": {

      "formats": ["markdown", "links"]

    }

  }'
```

### Response with Scraped Content

```
{

  "success": true,

  "data": [

    {

      "title": "Firecrawl - The Ultimate Web Scraping API",

      "description": "Firecrawl is a powerful web scraping API that turns any website into clean, structured data for AI and analysis.",

      "url": "https://firecrawl.dev/",

      "markdown": "# Firecrawl\n\nThe Ultimate Web Scraping API\n\n## Turn any website into clean, structured data\n\nFirecrawl makes it easy to extract data from websites for AI applications, market research, content aggregation, and more...",

      "links": [

        "https://firecrawl.dev/pricing",

        "https://firecrawl.dev/docs",

        "https://firecrawl.dev/guides",

        // ... more links

      ],

      "metadata": {

        "title": "Firecrawl - The Ultimate Web Scraping API",

        "description": "Firecrawl is a powerful web scraping API that turns any website into clean, structured data for AI and analysis.",

        "sourceURL": "https://firecrawl.dev/",

        "statusCode": 200

      }

    },

    // ... more results

  ]

}
```

Firecrawl’s search API supports various parameters to customize your search:

### Location Customization

```
curl -X POST https://api.firecrawl.dev/v1/search \

  -H "Content-Type: application/json" \

  -H "Authorization: Bearer fc-YOUR_API_KEY" \

  -d '{

    "query": "web scraping tools",

    "limit": 5,

    "location": "Germany"

  }'
```

Use the `tbs` parameter to filter results by time:

```
curl -X POST https://api.firecrawl.dev/v1/search \

  -H "Content-Type: application/json" \

  -H "Authorization: Bearer fc-YOUR_API_KEY" \

  -d '{

    "query": "latest web scraping techniques",

    "limit": 5,

    "tbs": "qdr:w"

  }'
```

Common `tbs` values:

- `qdr:h` - Past hour
- `qdr:d` - Past 24 hours
- `qdr:w` - Past week
- `qdr:m` - Past month
- `qdr:y` - Past year

### Custom Timeout

Set a custom timeout for search operations:

```
curl -X POST https://api.firecrawl.dev/v1/search \

  -H "Content-Type: application/json" \

  -H "Authorization: Bearer fc-YOUR_API_KEY" \

  -d '{

    "query": "complex search query",

    "limit": 10,

    "timeout": 30000

  }'
```

## Scraping Options

When scraping search results, you can specify multiple output formats:

```
curl -X POST https://api.firecrawl.dev/v1/search \

  -H "Content-Type: application/json" \

  -H "Authorization: Bearer fc-YOUR_API_KEY" \

  -d '{

    "query": "firecrawl features",

    "limit": 3,

    "scrapeOptions": {

      "formats": ["markdown", "html", "links", "screenshot"]

    }

  }'
```

Available formats:

- `markdown`: Clean, formatted markdown content
- `html`: Processed HTML content
- `rawHtml`: Unmodified HTML content
- `links`: List of links found on the page
- `screenshot`: Screenshot of the page
- `screenshot@fullPage`: Full-page screenshot
- `extract`: Structured data extraction

For more details about format options, refer to the [Scrape Feature documentation](https://docs.firecrawl.dev/features/scrape).

