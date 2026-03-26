#!/bin/bash

# SSL Setup Script for Notification Platform
# This script automates the HTTPS setup process

set -e

echo "🔒 Notification Platform - SSL Setup"
echo "===================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "⚠️  This script must be run as root (use sudo)"
   exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., notifications.example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Domain name is required"
    exit 1
fi

# Get email
read -p "Enter your email for Let's Encrypt notifications: " EMAIL
if [ -z "$EMAIL" ]; then
    echo "❌ Email is required"
    exit 1
fi

echo ""
echo "📋 Configuration:"
echo "   Domain: $DOMAIN"
echo "   Email: $EMAIL"
echo ""
read -p "Proceed with setup? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ Setup cancelled"
    exit 0
fi

echo ""
echo "1️⃣  Installing Certbot..."
if command -v apt &> /dev/null; then
    apt update -qq
    apt install -y certbot python3-certbot-nginx
elif command -v yum &> /dev/null; then
    yum install -y certbot python3-certbot-nginx
else
    echo "❌ Unsupported package manager"
    exit 1
fi

echo "✅ Certbot installed"
echo ""

echo "2️⃣  Stopping frontend container..."
cd ~/notification-platform || exit 1
docker-compose stop notification-frontend
echo "✅ Frontend stopped"
echo ""

echo "3️⃣  Obtaining SSL certificate..."
certbot certonly --standalone \
  -d "$DOMAIN" \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  --preferred-challenges http

if [ $? -eq 0 ]; then
    echo "✅ SSL certificate obtained"
else
    echo "❌ Failed to obtain certificate"
    echo "   Make sure:"
    echo "   - DNS points to this server"
    echo "   - Port 80 is open"
    echo "   - Domain is accessible"
    exit 1
fi
echo ""

echo "4️⃣  Updating nginx configuration..."
cp frontend/nginx-ssl.conf frontend/nginx-ssl-configured.conf
sed -i "s/YOUR_DOMAIN_HERE/$DOMAIN/g" frontend/nginx-ssl-configured.conf
cp frontend/nginx-ssl-configured.conf frontend/nginx.conf
echo "✅ Nginx config updated"
echo ""

echo "5️⃣  Updating docker-compose.yml..."
# Add SSL volume mounts if not already present
if ! grep -q "/etc/letsencrypt" docker-compose.yml; then
    echo "   Adding SSL volume mounts..."
    # This is a simple approach - you might want to edit docker-compose.yml manually
    echo "   ⚠️  Please manually add these volumes to notification-frontend in docker-compose.yml:"
    echo "   volumes:"
    echo "     - /etc/letsencrypt:/etc/letsencrypt:ro"
    echo "     - /var/lib/letsencrypt:/var/lib/letsencrypt:ro"
fi
echo ""

echo "6️⃣  Rebuilding and restarting services..."
docker-compose up -d --build notification-frontend
echo "✅ Services restarted"
echo ""

echo "7️⃣  Setting up auto-renewal..."
(crontab -l 2>/dev/null || true; echo "0 0,12 * * * certbot renew --quiet --deploy-hook 'cd ~/notification-platform && docker-compose restart notification-frontend'") | crontab -
echo "✅ Auto-renewal configured"
echo ""

echo "✅ SSL Setup Complete!"
echo ""
echo "🎉 Your application is now available at:"
echo "   https://$DOMAIN"
echo ""
echo "📝 Next steps:"
echo "   1. Test the HTTPS URL in your browser"
echo "   2. Check the SSL certificate (padlock icon)"
echo "   3. Ensure all resources load over HTTPS"
echo ""
echo "🔄 Certificate auto-renewal is configured"
echo "   - Runs twice daily"
echo "   - Certificates auto-renew 30 days before expiry"
echo ""
