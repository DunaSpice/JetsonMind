# VibeDeployer Server Setup Documentation

**Date**: August 5, 2025  
**Server**: Ubuntu 22.04 on ARM64 (Jetson/Tegra)  
**Public IP**: 157.131.100.4  
**Local IP**: 192.168.0.251  

## Overview

This document covers the complete setup of vibedeployer.com server with SSH access, web hosting using Caddy, and Cloudflare integration.

## 🎯 Final Configuration

### Services Running
- **SSH Server**: OpenSSH on port 22
- **Web Server**: Caddy 2.10.0 with automatic HTTPS
- **Website**: Hello World page at https://vibedeployer.com
- **Cloudflare Tunnel**: cloudflared 2025.7.0 (eliminates dynamic IP issues)
- **DNS**: Cloudflare proxy with tunnel routing

### Access Points
- **Website**: https://vibedeployer.com ✅ (via Cloudflare Tunnel)
- **SSH Access**: `ssh petr@ssh.vibedeployer.com` ✅ (via Cloudflare Tunnel)
- **Direct IP SSH**: `ssh petr@157.131.100.4` ✅ (fallback, requires port forwarding)

## 📋 Step-by-Step Setup Process

### 1. System Preparation

```bash
# Configure passwordless sudo
echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$USER

# Update package lists
sudo apt update
```

### 2. SSH Server Configuration

**Status**: SSH was already installed and running
- **Service**: ssh.service (active)
- **Port**: 22 (default)
- **Authentication**: Public key authentication enabled
- **Location**: /etc/ssh/sshd_config

**Authorized Keys**: Located at `/home/petr/.ssh/authorized_keys`
- Contains Ed25519 and RSA keys for authentication
- Keys from petr@mail.iai.my and p@2p3.io

### 3. Caddy Web Server Installation

```bash
# Install prerequisites
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

# Add Caddy repository
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

# Install Caddy
sudo apt update && sudo apt install caddy
```

### 4. Website Content Creation

**Directory Structure**:
```
/var/www/vibedeployer/
└── index.html
```

**Content**: Hello World page with:
- Responsive design
- Gradient background
- "Created by vibedeployer.com" footer
- Security headers integration

### 5. Caddy Configuration

**Final Caddyfile** (`/etc/caddy/Caddyfile`):
```caddy
vibedeployer.com {
    root * /var/www/vibedeployer
    file_server
    
    header {
        X-Content-Type-Options nosniff
        X-XSS-Protection "1; mode=block"
        X-Frame-Options DENY
        -Server
    }
    
    log {
        output file /var/log/caddy/vibedeployer.log
    }
}

www.vibedeployer.com {
    redir https://vibedeployer.com{uri} permanent
}
```

**Key Features**:
- Automatic HTTPS with Let's Encrypt
- Security headers (HSTS, XSS protection, etc.)
- WWW to non-WWW redirect
- Access logging to `/var/log/caddy/vibedeployer.log`

### 6. Network Configuration

**Router Port Forwarding** (configured at 192.168.0.1):
- Port 22 (SSH) → 192.168.0.251:22
- Port 80 (HTTP) → 192.168.0.251:80  
- Port 443 (HTTPS) → 192.168.0.251:443

### 7. Cloudflare Tunnel Setup

**Purpose**: Eliminates dynamic IP dependency and port forwarding requirements.

```bash
# Download and install cloudflared
curl -L --output /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i /tmp/cloudflared.deb

# Authenticate with Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create vibedeployer

# Configure tunnel
sudo mkdir -p /etc/cloudflared
sudo cp ~/.cloudflared/config.yml /etc/cloudflared/
sudo cp ~/.cloudflared/b4ae1c81-1299-42ba-8fea-f89491c15c9f.json /etc/cloudflared/

# Install and start service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

**Tunnel Configuration** (`/etc/cloudflared/config.yml`):
```yaml
tunnel: b4ae1c81-1299-42ba-8fea-f89491c15c9f
credentials-file: /etc/cloudflared/b4ae1c81-1299-42ba-8fea-f89491c15c9f.json

ingress:
  - hostname: vibedeployer.com
    service: http://localhost:80
  - hostname: ssh.vibedeployer.com
    service: ssh://localhost:22
  - service: http_status:404
```

**Key Benefits**:
- **No Dynamic IP Issues**: Tunnel connects outbound to Cloudflare
- **No Port Forwarding**: Router NAT configuration not required
- **Enhanced Security**: Traffic encrypted end-to-end through tunnel
- **Automatic Failover**: Multiple tunnel connections for redundancy

### 8. Cloudflare DNS Configuration

**DNS Records** (Updated for Tunnel):
| Type | Name | Target | Proxy Status | Notes |
|------|------|--------|--------------|-------|
| CNAME | vibedeployer.com | b4ae1c81-1299-42ba-8fea-f89491c15c9f.cfargotunnel.com | ✅ Proxied | Tunnel routing |
| CNAME | ssh.vibedeployer.com | b4ae1c81-1299-42ba-8fea-f89491c15c9f.cfargotunnel.com | ✅ Proxied | SSH via tunnel |
| CNAME | www.vibedeployer.com | vibedeployer.com | ✅ Proxied | WWW redirect |

**Legacy DNS Records** (Now unnecessary):
| Type | Name | Target | Status |
|------|------|--------|--------|
| A | vibedeployer.com | 157.131.100.4 | ❌ Replaced by tunnel |
| A | ssh.vibedeployer.com | 157.131.100.4 | ❌ Replaced by tunnel |

**SSL/TLS Mode**: Full (automatic)
- Cloudflare terminates SSL
- Origin uses Let's Encrypt certificates
- Automatic HTTP to HTTPS redirect

## 🔧 Troubleshooting Steps Taken

### Issue 1: SSL Handshake Failed (HTTP 521/525)

**Problem**: Cloudflare couldn't establish SSL connection with origin server.

**Root Cause**: Caddy was configured with catch-all `:80` instead of specific domain.

**Solution**: 
1. Updated Caddyfile to use `vibedeployer.com` instead of `:80`
2. Let Caddy automatically obtain SSL certificates for the domain
3. Cloudflare's "Full" SSL mode now works correctly

### Issue 2: SSH Connection Refused

**Problem**: External SSH connections were refused despite SSH service running.

**Root Cause**: Router NAT wasn't forwarding port 22 to the server.

**Solution**: Configured port forwarding on router (192.168.0.1).

## 📊 System Status

### Services Status
```bash
# Check SSH
sudo systemctl status ssh

# Check Caddy  
sudo systemctl status caddy

# Check ports
sudo ss -tlnp | grep -E ':22|:80|:443'
```

### File Locations
- **Website Files**: `/var/www/vibedeployer/`
- **Caddy Config**: `/etc/caddy/Caddyfile`
- **Caddy Logs**: `/var/log/caddy/vibedeployer.log`
- **SSH Config**: `/etc/ssh/sshd_config`
- **Authorized Keys**: `/home/petr/.ssh/authorized_keys`

### Testing Commands
```bash
# Test website
curl -I https://vibedeployer.com
curl -I http://vibedeployer.com  # Should redirect to HTTPS

# Test SSH
ssh petr@ssh.vibedeployer.com
ssh petr@157.131.100.4

# Test ports
nc -zv 157.131.100.4 22
nc -zv 157.131.100.4 80
nc -zv 157.131.100.4 443
```

## 🔐 Security Configuration

### Implemented Security Measures
1. **SSH**: Key-based authentication only
2. **HTTPS**: Automatic SSL certificates with HSTS
3. **Security Headers**: 
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: 1; mode=block
   - X-Frame-Options: DENY
   - Server header removed
4. **Cloudflare Protection**: DDoS protection and Web Application Firewall
5. **Passwordless Sudo**: Configured for deployment automation

### Firewall Status
- **UFW**: Not installed (using router-level filtering)
- **iptables**: Default ACCEPT policy (protected by router NAT)

## 🚀 Deployment Information

### Server Specifications
- **OS**: Ubuntu 22.04.4 LTS
- **Architecture**: ARM64 (aarch64)
- **Platform**: NVIDIA Jetson (Tegra SoC)
- **Kernel**: Linux 5.15.148-tegra
- **Memory**: 8GB limit configured
- **Network**: Gigabit Ethernet via enP8p1s0

### Software Versions
- **Caddy**: 2.10.0
- **OpenSSH**: 8.9p1 Ubuntu-3ubuntu0.10
- **curl**: 7.81.0
- **Node.js**: 22.x (available)
- **Docker**: Installed and running

## 📝 Maintenance Notes

### Log Monitoring
```bash
# Monitor Caddy logs
sudo tail -f /var/log/caddy/vibedeployer.log

# Monitor SSH connections
sudo journalctl -u ssh -f

# Monitor Caddy service
sudo journalctl -u caddy -f
```

### SSL Certificate Renewal
- **Automatic**: Caddy handles Let's Encrypt renewal automatically
- **Manual check**: Certificates visible in `/var/lib/caddy/.local/share/caddy/certificates/`

### Backup Recommendations
1. **Website content**: `/var/www/vibedeployer/`
2. **Caddy configuration**: `/etc/caddy/Caddyfile`
3. **SSH keys**: `/home/petr/.ssh/`
4. **SSL certificates**: `/var/lib/caddy/` (auto-renewable)

## 🔄 Future Enhancements

### Suggested Improvements
1. **Monitoring**: Set up system monitoring (Prometheus/Grafana)
2. **Backup**: Automated backup system
3. **CI/CD**: GitHub Actions for deployment
4. **Database**: PostgreSQL/MySQL for dynamic content
5. **Caching**: Redis for session management
6. **Load Balancing**: Multiple server instances

### Scaling Options
1. **Horizontal**: Add more Jetson devices behind load balancer
2. **Vertical**: Upgrade to higher-spec Jetson models
3. **Cloud**: Hybrid cloud deployment with Cloudflare Workers

---

**Setup Completed**: August 5, 2025  
**Documentation Created**: August 5, 2025  
**Status**: ✅ Production Ready

*This server was configured by Claude Code for vibedeployer.com*