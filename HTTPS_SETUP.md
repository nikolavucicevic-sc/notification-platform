# HTTPS Setup Guide for Notification Platform

This guide will help you set up HTTPS with a proper domain name and SSL certificate.

## Prerequisites

1. **Domain Name** - You need to own a domain (e.g., `example.com`)
2. **EC2 Public IP** - Your current IP: `18.156.176.60`
3. **EC2 Security Group** - Must allow ports 80 and 443

## Step 1: Get a Domain Name

### Option A: Buy a domain
- **Namecheap**: ~$10-15/year
- **GoDaddy**: ~$12-20/year
- **Google Domains**: ~$12/year
- **AWS Route 53**: ~$12/year (integrates well with EC2)

### Option B: Use a free subdomain (for testing)
- **FreeDNS** (freedns.afraid.org)
- **DuckDNS** (duckdns.org)
- **No-IP** (noip.com)

## Step 2: Point DNS to Your EC2

Once you have a domain (e.g., `notifications.example.com`):

1. Log into your DNS provider
2. Create an **A Record**:
   ```
   Type: A
   Name: notifications (or @ for root domain)
   Value: 18.156.176.60
   TTL: 300 (or automatic)
   ```
3. Wait 5-60 minutes for DNS propagation
4. Test: `nslookup notifications.example.com`

## Step 3: Update EC2 Security Group

Ensure your EC2 security group allows:
```
Port 80 (HTTP)   - 0.0.0.0/0
Port 443 (HTTPS) - 0.0.0.0/0
Port 22 (SSH)    - Your IP
```

## Step 4: Install Certbot on EC2

SSH into your EC2 instance and run:

```bash
# Update system
sudo apt update

# Install Certbot and nginx plugin
sudo apt install certbot python3-certbot-nginx -y

# Or for Amazon Linux:
sudo yum install certbot python3-certbot-nginx -y
```

## Step 5: Stop Docker Frontend (Temporary)

Certbot needs port 80 to verify domain ownership:

```bash
cd ~/notification-platform
docker-compose stop notification-frontend
```

## Step 6: Get SSL Certificate

Replace `notifications.example.com` with your actual domain:

```bash
sudo certbot certonly --standalone \
  -d notifications.example.com \
  --non-interactive \
  --agree-tos \
  --email your-email@example.com
```

This will create certificates at:
- `/etc/letsencrypt/live/notifications.example.com/fullchain.pem`
- `/etc/letsencrypt/live/notifications.example.com/privkey.pem`

## Step 7: Update Docker Compose

Add SSL volume mounts to `docker-compose.yml`:

```yaml
  notification-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"  # Add HTTPS port
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro  # SSL certificates
      - /var/lib/letsencrypt:/var/lib/letsencrypt:ro
    depends_on:
      notification-service:
        condition: service_started
      customer-service:
        condition: service_started
    networks:
      - notification-network
```

## Step 8: Update Nginx Config

The SSL-enabled nginx config will be created automatically. Check `frontend/nginx-ssl.conf` in the repo.

## Step 9: Restart Services

```bash
cd ~/notification-platform
git pull origin main
docker-compose up -d --build notification-frontend
```

## Step 10: Set Up Auto-Renewal

Let's Encrypt certificates expire after 90 days. Set up auto-renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e

# Add this line (runs twice daily):
0 0,12 * * * certbot renew --quiet --deploy-hook "cd /home/ubuntu/notification-platform && docker-compose restart notification-frontend"
```

## Verification

After setup:

1. Visit `https://notifications.example.com` (note the `s`)
2. Check the padlock icon in browser
3. Verify certificate details
4. Test mixed content (all resources should be HTTPS)

## Troubleshooting

### DNS not resolving
```bash
# Check DNS propagation
nslookup notifications.example.com
dig notifications.example.com
```

### Certificate generation failed
```bash
# Check logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Common issues:
# - Port 80 blocked
# - Domain doesn't point to server
# - Docker still running on port 80
```

### Mixed content warnings
- Ensure all API calls use relative URLs (`/api/...`)
- Check browser console for HTTP resources
- Update `X-Forwarded-Proto` headers

## Cost Breakdown

- **Domain**: $10-15/year
- **SSL Certificate**: FREE (Let's Encrypt)
- **EC2**: Your existing costs
- **Total**: ~$10-15/year

## Alternative: Cloudflare (Easier Option)

If you want an even easier setup:

1. Buy domain anywhere (or use existing)
2. Add site to Cloudflare (free plan)
3. Update nameservers to Cloudflare
4. In Cloudflare DNS: Add A record pointing to `18.156.176.60`
5. Enable "Full (strict)" SSL in Cloudflare
6. Get Cloudflare Origin Certificate
7. Install origin cert on nginx

Benefits:
- Free SSL
- DDoS protection
- CDN
- Easier management

## Next Steps

Once you decide on a domain, I can:
1. Create the SSL-enabled nginx configuration
2. Update the docker-compose.yml
3. Create automated setup scripts
4. Configure HSTS and security headers

Let me know what domain you choose or if you want to use Cloudflare!
