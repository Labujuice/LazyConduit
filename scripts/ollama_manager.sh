#!/bin/bash

# Ollama Service Manager for LazyConduit
# Handles starting, stopping, and checking the status of Ollama service.

COMMAND=$1

case $COMMAND in
    start)
        echo "Starting Ollama service..."
        if pgrep -x "ollama" > /dev/null; then
            echo "Ollama is already running."
        else
            # Try systemctl first, fallback to background process
            if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet ollama; then
                echo "Ollama systemd service is already active."
            elif command -v systemctl >/dev/null 2>&1; then
                sudo systemctl start ollama && echo "Ollama service started via systemctl." || {
                    echo "Failed to start via systemctl, trying manual background start..."
                    ollama serve > /dev/null 2>&1 &
                }
            else
                ollama serve > /dev/null 2>&1 &
                echo "Ollama started in background."
            fi
        fi
        ;;
    stop)
        echo "Stopping Ollama service..."
        if command -v systemctl >/dev/null 2>&1; then
            sudo systemctl stop ollama && echo "Ollama service stopped via systemctl."
        fi
        pkill -x "ollama" && echo "Ollama process killed." || echo "No ollama process found."
        ;;
    status)
        if pgrep -x "ollama" > /dev/null; then
            echo "Status: Running"
            exit 0
        else
            echo "Status: Stopped"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
