#!/bin/bash

# Build script for the React frontend

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
UI_DIR="$PROJECT_ROOT/ui"

echo "🔨 Building React ui for Django..."

# Check if ui directory exists
if [ ! -d "$UI_DIR" ]; then
    echo "❌ Frontend directory not found!"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "$UI_DIR/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd "$UI_DIR" && npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error running: npm install"
        exit 1
    fi
    echo "✅ npm install"
fi

# Build the frontend
echo "⚡ Building with Vite..."
cd "$UI_DIR" && npm run build
if [ $? -ne 0 ]; then
    echo "❌ Error running: npm run build"
    exit 1
fi
echo "✅ npm run build"

# Check if build was successful
DIST_DIR="$PROJECT_ROOT/static/dist"
if [ -d "$DIST_DIR" ]; then
    echo "✅ Frontend built successfully!"
    echo "📁 Build output: $DIST_DIR"
    
    # List built files
    echo "Built files:"
    find "$DIST_DIR" -type f | while read -r file; do
        echo "   - ${file#$DIST_DIR/}"
    done
else
    echo "❌ Build failed - no dist directory found"
    exit 1
fi
