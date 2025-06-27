#!/usr/bin/env python3
"""
Build script for the React frontend
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build function"""
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    
    print("🔨 Building React frontend for Django...")
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        sys.exit(1)
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing dependencies...")
        if not run_command("npm install", cwd=frontend_dir):
            sys.exit(1)
    
    # Build the frontend
    print("⚡ Building with Vite...")
    if not run_command("npm run build", cwd=frontend_dir):
        sys.exit(1)
    
    # Check if build was successful
    dist_dir = project_root / "static" / "dist"
    if dist_dir.exists():
        print(f"✅ Frontend built successfully!")
        print(f"📁 Build output: {dist_dir}")
        
        # List built files
        for file in dist_dir.rglob("*"):
            if file.is_file():
                print(f"   - {file.relative_to(dist_dir)}")
    else:
        print("❌ Build failed - no dist directory found")
        sys.exit(1)

if __name__ == "__main__":
    main()