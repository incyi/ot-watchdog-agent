#!/bin/bash

# OT Watchdog Agent - Helper Script
# Usage: ./start.sh [start|stop|logs|build]

set -e

COMMAND=${1:-help}

case $COMMAND in
  start)
    echo "🚀 Starting OT Watchdog Stack..."
    docker-compose up -d
    echo "✅ Stack started!"
    echo ""
    echo "📋 Services:"
    echo "  - WordPress: http://localhost:8000"
    echo "  - MySQL: localhost:3306"
    echo "  - Agent: Running in container"
    echo ""
    echo "🔍 View logs: docker-compose logs -f"
    ;;
  
  stop)
    echo "🛑 Stopping OT Watchdog Stack..."
    docker-compose down
    echo "✅ Stack stopped!"
    ;;
  
  logs)
    echo "📜 Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f
    ;;
  
  build)
    echo "🔨 Building OT Watchdog Agent image..."
    docker-compose build --no-cache
    echo "✅ Build complete!"
    ;;
  
  restart)
    echo "🔄 Restarting OT Watchdog Stack..."
    docker-compose restart
    echo "✅ Stack restarted!"
    ;;
  
  status)
    echo "📊 Container Status:"
    docker-compose ps
    ;;
  
  clean)
    echo "🧹 Removing containers and volumes..."
    docker-compose down -v
    echo "✅ Cleaned!"
    ;;
  
  *)
    echo "OT Watchdog Agent - Docker Helper"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the stack (WordPress + MySQL + Agent)"
    echo "  stop     - Stop the stack"
    echo "  restart  - Restart the stack"
    echo "  logs     - View logs (follow mode)"
    echo "  status   - Show container status"
    echo "  build    - Build Docker image"
    echo "  clean    - Remove containers and volumes"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start everything"
    echo "  $0 logs      # View live logs"
    echo "  $0 build     # Rebuild image"
    ;;
esac
