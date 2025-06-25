# Ruby Bot Deployment Guide

## 🚀 Secure Deployment with MTProxy Support

This Ruby Bot is configured for Vietnam Telegram unblock using MTProxy and environment variables.

## 📋 Required Environment Variables

```bash
# Required secrets (create manually in Kubernetes)
BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
MTPROXY_SECRET="YOUR_MTPROXY_SECRET_HERE"

# Optional configuration
MTPROXY_HOST="t.segfault.net"          # MTProxy server
MTPROXY_PORT="8443"                    # MTProxy port
ADB_DEVICE_IP="192.168.1.100"           # Android device IP
VIDEO_PATH="/storage/self/primary/video/spa_noaudio.mp4"
SOCKS_PROXY="socks5://proxy:1080"      # Optional SOCKS proxy for bot
```

## 🔐 Kubernetes Deployment

### Method 1: Using deploy.sh script (Recommended)

1. **Setup environment:**
```bash
# Copy template and fill with your secrets
cp .env.example .env
# Edit .env with your actual BOT_TOKEN and MTPROXY_SECRET
```

2. **Deploy automatically:**
```bash
./deploy.sh
```

### Method 2: Manual deployment

1. **Create secrets manually:**
```bash
kubectl create secret generic ruby-bot-secrets \
  --from-literal=bot-token="YOUR_BOT_TOKEN" \
  --from-literal=mtproxy-secret="YOUR_MTPROXY_SECRET" \
  -n ruby-bot
```

2. **Deploy with Helm:**
```bash
helm upgrade --install ruby-bot ./ruby-bot \
  --namespace ruby-bot \
  --create-namespace \
  --set image.tag="latest"
```

3. **Check deployment:**
```bash
kubectl get pods -n ruby-bot
kubectl logs -f deployment/ruby-bot -n ruby-bot
```

## 🌐 MTProxy Configuration

For Telegram client use this link:
```
tg://proxy?server=t.segfault.net&port=8443&secret=YOUR_SECRET
```

## 📱 Bot Commands

- `/start` - Welcome message with proxy status
- `/set_landscape` - Set landscape orientation
- `/set_portrait` - Set portrait orientation  
- `/play_video` - Play video on device
- `/adb_connect` - Connect to ADB device
- `/check_proxy` - Check proxy status

## 🔒 Security Notes

- ✅ No secrets in code or Git history
- ✅ All sensitive data via environment variables
- ✅ Secure Kubernetes secret management
- ✅ MTProxy link for client configuration 