"""
API Startup Script
Simple script to start the Research API with checks
"""

import os
import sys
import subprocess
import socket
import time


def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✓ Redis is running")
        return True
    except ImportError:
        print("✗ Redis package not installed. Run: pip install redis")
        return False
    except Exception as e:
        print(f"✗ Redis is not running. Start it with:")
        print("  macOS: brew services start redis")
        print("  Linux: sudo systemctl start redis-server")
        print("  Docker: docker run -d -p 6379:6379 redis:latest")
        return False


def check_ollama():
    """Check if Ollama is available"""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Ollama is installed")

            # Check for llama3.2
            if 'llama3.2' in result.stdout:
                print("✓ llama3.2 model available")
                return True
            else:
                print("⚠ llama3.2 model not found. Run: ollama pull llama3.2")
                print("  (API will still work with other models)")
                return True
        else:
            print("✗ Ollama not installed. Install from: https://ollama.ai")
            print("  Alternatively, set LLM_PROVIDER=openai and OPENAI_API_KEY")
            return False
    except FileNotFoundError:
        print("✗ Ollama not found in PATH")
        print("  Install from: https://ollama.ai")
        print("  Alternatively, set LLM_PROVIDER=openai and OPENAI_API_KEY")
        return False
    except Exception as e:
        print(f"⚠ Could not check Ollama: {e}")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'fastapi',
        'uvicorn',
        'redis',
        'crewai',
        'langchain',
        'yfinance'
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print(f"  Run: pip install -r src/api/requirements.txt")
        return False
    else:
        print(f"✓ All required packages installed")
        return True


def check_port(port=8000):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
        print(f"✓ Port {port} is available")
        return True
    except OSError:
        print(f"✗ Port {port} is already in use")
        print(f"  Kill process using port: lsof -ti:{port} | xargs kill -9")
        return False


def start_api(host='0.0.0.0', port=8000, reload=True):
    """Start the FastAPI server"""
    print("\n" + "="*60)
    print("Starting Research API")
    print("="*60 + "\n")

    # Pre-flight checks
    checks = [
        check_dependencies(),
        check_redis(),
        check_ollama(),
        check_port(port)
    ]

    if not all(checks):
        print("\n✗ Pre-flight checks failed. Please fix the issues above.")
        sys.exit(1)

    print("\n✓ All checks passed. Starting API...\n")

    # Set environment
    os.environ.setdefault('LLM_PROVIDER', 'ollama')
    os.environ.setdefault('LLM_MODEL', 'llama3.2')

    # Start uvicorn
    try:
        cmd = [
            'uvicorn',
            'src.api.research_endpoints:app',
            '--host', host,
            '--port', str(port)
        ]

        if reload:
            cmd.append('--reload')

        print(f"Command: {' '.join(cmd)}\n")
        print("="*60)
        print(f"API running at: http://localhost:{port}")
        print(f"Docs available at: http://localhost:{port}/docs")
        print(f"ReDoc available at: http://localhost:{port}/redoc")
        print("="*60)
        print("\nPress Ctrl+C to stop\n")

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n\nShutting down API...")
    except Exception as e:
        print(f"\n✗ Failed to start API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Start Research API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')

    args = parser.parse_args()

    start_api(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )
