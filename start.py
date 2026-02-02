#!/usr/bin/env python3
"""
Startup script for MTU Web Interface
"""
import os
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)