#!/usr/bin/env python
"""
Run the Django application with Daphne ASGI server for proper SSE streaming support.
"""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Knowmore.settings")
    
    # Run with Daphne
    from daphne.cli import CommandLineInterface
    
    # Run on port 8000
    sys.argv = ["daphne", "-b", "127.0.0.1", "-p", "8000", "Knowmore.asgi:application"]
    
    cli = CommandLineInterface()
    cli.run(sys.argv[1:])