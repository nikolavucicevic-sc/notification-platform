#!/bin/bash

# Script to tail logs from all services

if [ -z "$1" ]; then
    echo "Usage: ./logs.sh [service]"
    echo ""
    echo "Available services:"
    echo "  all                - All services"
    echo "  notification       - Notification service"
    echo "  customer           - Customer service"
    echo "  email              - Email sender"
    echo "  frontend           - Frontend"
    exit 1
fi

case "$1" in
    all)
        tail -f logs/*.log
        ;;
    notification)
        tail -f logs/notification-service.log
        ;;
    customer)
        tail -f logs/customer-service.log
        ;;
    email)
        tail -f logs/email-sender.log
        ;;
    frontend)
        tail -f logs/frontend.log
        ;;
    *)
        echo "Unknown service: $1"
        exit 1
        ;;
esac
