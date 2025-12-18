# AVA Platform - Complete Render Deployment Guide

## 🎯 Overview

This guide deploys the **complete AVA platform** to Render:
1. **PostgreSQL Database** (70+ tables with TimescaleDB)
2. **Redis Cache** (for data caching and queuing)
3. **FastAPI Research API** (port 8000) - AI research endpoints
4. **Telegram Webhook Server** (optional) - Bot webhook endpoint

**Total Monthly Cost**: ~$17-22/month (vs. running locally with reliability issues)

---

## 📋 What You Need from Render

### Prerequisites
1. **Render Account**: [Sign up at render.com](https://render.com)
2. **GitHub Account**: Connect to Render for auto-deployment
3. **Credit Card**: Required for paid plans (starts at $7/month)

### From Render Dashboard, You'll Get:
- ✅ PostgreSQL connection string
- ✅ Redis connection string
- ✅ Public HTTPS URLs for APIs
- ✅ Environment variable management
- ✅ Automatic SSL certificates
- ✅ Logs and monitoring

---

## 🚀 Step-by-Step Deployment

### STEP 1: Deploy PostgreSQL Database

#### 1.1 Create PostgreSQL Instance
```
1. Go to Render Dashboard: https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: ava-trading-db
   - Database: trading
   - User: ava_user (or your choice)
   - Region: Oregon (or closest to you)
   - PostgreSQL Version: 16
   - Plan: Starter ($7/month)
     ✅ 10GB storage
     ✅ 1GB RAM
     ✅ Daily backups (7-day retention)
     ✅ Point-in-time recovery
4. Click "Create Database"
5. Wait 2-3 minutes for provisioning
```

#### 1.2 Enable TimescaleDB Extension
Once database is ready:
```
1. Click "Connect" → "PSQL Command"
2. Run:
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

#### 1.3 Get Connection Details
Render provides these automatically:
- **Internal Connection String**: For services within Render
- **External Connection String**: For external connections
- **PSQL Command**: Direct database access

**Save these** - you'll need them for deployment and .env configuration.

Example External Connection String:
```
postgresql://ava_user:abc123xyz@dpg-xxx-a.oregon-postgres.render.com:5432/trading
```

---

### STEP 2: Deploy Redis Cache

#### 2.1 Create Redis Instance
```
1. Render Dashboard → "New +" → "Redis"
2. Configure:
   - Name: ava-redis-cache
   - Plan: Free (25MB, perfect for caching)
     OR Starter ($10/month, 100MB + persistence)
   - Region: Same as PostgreSQL (Oregon)
3. Click "Create Redis"
```

#### 2.2 Get Connection Details
```
Internal Redis URL: redis://red-xxx:6379
External Redis URL: redis://red-xxx-a.oregon-redis.render.com:6379
```

**Save these** for environment configuration.

---

### STEP 3: Deploy FastAPI Research API

#### 3.1 Prepare for Deployment
Create `render.yaml` in your repo root:
```yaml
services:
  - type: web
    name: ava-research-api
    runtime: python
    plan: starter  # $7/month
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.api.research_endpoints:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DB_HOST
        fromDatabase:
          name: ava-trading-db
          property: host
      - key: DB_PORT
        fromDatabase:
          name: ava-trading-db
          property: port
      - key: DB_NAME
        fromDatabase:
          name: ava-trading-db
          property: database
      - key: DB_USER
        fromDatabase:
          name: ava-trading-db
          property: user
      - key: DB_PASSWORD
        fromDatabase:
          name: ava-trading-db
          property: password
      - key: REDIS_HOST
        fromDatabase:
          name: ava-redis-cache
          property: host
      - key: REDIS_PORT
        fromDatabase:
          name: ava-redis-cache
          property: port
      - key: REDIS_DB
        value: "0"
      - key: LLM_PROVIDER
        value: "ollama"
      - key: LLM_MODEL
        value: "llama3.2"
    healthCheckPath: /health
```

#### 3.2 Deploy via GitHub (Recommended)
```
1. Push code to GitHub
2. Render Dashboard → "New +" → "Web Service"
3. Connect your GitHub repository
4. Render auto-detects render.yaml
5. Click "Create Web Service"
6. Render builds and deploys automatically
```

**OR** Manual Deploy:
```
1. "New +" → "Web Service"
2. Select "Deploy from Git"
3. Choose repository
4. Manual settings:
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn src.api.research_endpoints:app --host 0.0.0.0 --port $PORT
   - Plan: Starter ($7/month)
5. Add environment variables (from Step 1 & 2)
6. Deploy
```

#### 3.3 Get API URL
After deployment:
```
Public URL: https://ava-research-api.onrender.com
API Docs: https://ava-research-api.onrender.com/docs
```

---

### STEP 4: Deploy Telegram Webhook Server (Optional)

Only needed if using Telegram bot with webhooks.

#### 4.1 Create Web Service
```
1. Render Dashboard → "New +" → "Web Service"
2. Configure:
   - Name: ava-telegram-webhook
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn src.ava.webhook_server:app --host 0.0.0.0 --port $PORT
   - Plan: Free (spins down after inactivity)
     OR Starter ($7/month, always on)
```

#### 4.2 Environment Variables
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_SECRET_TOKEN=your_webhook_secret
REDIS_URL=<from Step 2>
TELEGRAM_USE_WEBHOOKS=true
```

#### 4.3 Set Telegram Webhook
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://ava-telegram-webhook.onrender.com/webhook"
```

---

### STEP 5: Deploy Database Schema

Now that infrastructure is ready, deploy the schema.

#### 5.1 From Your Local Machine
```bash
cd c:\Code\Legion\repos\ava

# Deploy master schema to Render
scripts\deploy_to_render.bat

# When prompted, paste your PostgreSQL External Connection String
# Wait ~30 seconds for deployment
```

**What Gets Deployed:**
- ✅ 70+ tables (all features)
- ✅ 10+ views for common queries
- ✅ 5+ functions and triggers
- ✅ 40+ performance indexes
- ✅ TimescaleDB hypertables
- ✅ Initial configuration data

---

### STEP 6: Update Local Environment

#### 6.1 Update .env File
```bash
python scripts/update_env_for_render.py

# Paste your Render PostgreSQL connection string
```

**OR** Manual Update:
```env
# PostgreSQL (Render)
DB_HOST=dpg-xxx-a.oregon-postgres.render.com
DB_PORT=5432
DB_NAME=trading
DB_USER=ava_user
DB_PASSWORD=abc123xyz

DATABASE_URL=postgresql://ava_user:abc123@dpg-xxx.oregon-postgres.render.com/trading

# Redis (Render)
REDIS_HOST=red-xxx-a.oregon-redis.render.com
REDIS_PORT=6379
REDIS_DB=0

# API Endpoints (Render)
RESEARCH_API_URL=https://ava-research-api.onrender.com
WEBHOOK_API_URL=https://ava-telegram-webhook.onrender.com
```

#### 6.2 Test Connections
```bash
# Test PostgreSQL
scripts\test_render_connection.bat

# Test Redis
python -c "import redis; r = redis.Redis(host='your-redis-host', port=6379); print('✅ Redis OK' if r.ping() else '❌ Redis Failed')"

# Test API
curl https://ava-research-api.onrender.com/health
```

---

## 💰 Cost Breakdown

### Option 1: Minimal Setup (Everything Running)
| Service | Plan | Cost |
|---------|------|------|
| PostgreSQL | Starter | $7/month |
| Redis | Free | $0/month |
| Research API | Starter | $7/month |
| Telegram Webhook | Free | $0/month |
| **Total** | | **$14/month** |

**Notes:**
- Free Redis has 25MB (sufficient for caching)
- Free Web Service spins down after 15min inactivity
- Cold start takes ~30 seconds

### Option 2: Production Setup (Always On)
| Service | Plan | Cost |
|---------|------|------|
| PostgreSQL | Starter | $7/month |
| Redis | Starter | $10/month |
| Research API | Starter | $7/month |
| Telegram Webhook | Starter | $7/month |
| **Total** | | **$31/month** |

**Benefits:**
- ✅ No cold starts (instant response)
- ✅ Redis persistence (data survives restarts)
- ✅ 100MB Redis (more cache capacity)
- ✅ 24/7 availability

### Option 3: High Performance
| Service | Plan | Cost |
|---------|------|------|
| PostgreSQL | Pro ($65) | $65/month |
| Redis | Pro ($20) | $20/month |
| Research API | Standard ($25) | $25/month |
| **Total** | | **$110/month** |

**Benefits:**
- ✅ 256GB PostgreSQL storage
- ✅ 4GB RAM (much faster queries)
- ✅ 1GB Redis (handles heavy load)
- ✅ High availability & failover

---

## 🔒 Security Configuration

### Environment Variables Management
Render provides secure environment variable storage:
```
1. Each service has "Environment" tab
2. Add variables (encrypted at rest)
3. Variables auto-injected at runtime
4. Change without redeployment
```

### Recommended Security:
- ✅ Use Render's secret management (don't commit .env)
- ✅ Enable SSL (automatic on Render)
- ✅ Restrict database connections (use Internal URLs when possible)
- ✅ Set up IP allowlisting for PostgreSQL (optional)
- ✅ Rotate secrets regularly

---

## 📊 Monitoring & Logs

### Render Dashboard Features:
```
1. Metrics Tab:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

2. Logs Tab:
   - Real-time log streaming
   - Filter by level (INFO, ERROR, etc.)
   - Download logs

3. Events Tab:
   - Deployments history
   - Scaling events
   - Health check failures
```

### Set Up Alerts:
```
1. Service → Settings → Notifications
2. Add email/Slack webhook
3. Configure alerts:
   - Deployment failures
   - High error rate
   - Health check failures
   - High CPU/memory usage
```

---

## 🔄 CI/CD Pipeline

### Automatic Deployments:
Render auto-deploys on git push:
```
1. Push code to GitHub main branch
2. Render detects changes
3. Builds application
4. Runs tests (if configured)
5. Deploys to production
6. Health checks verify deployment
```

### Rollback:
```
1. Render Dashboard → Service → Events
2. Find previous successful deployment
3. Click "Redeploy"
4. Instant rollback to known-good state
```

---

## 🛠️ Troubleshooting

### Issue: Build Fails
**Solution:**
```bash
# Check requirements.txt has correct versions
# Look for conflicting dependencies
pip install -r requirements.txt  # Test locally first
```

### Issue: Database Connection Timeout
**Solution:**
- Use Internal Connection String for services within Render
- Check firewall settings (Render → PostgreSQL → Settings → Connections)
- Verify environment variables are set correctly

### Issue: Redis Connection Refused
**Solution:**
- Free Redis sleeps after inactivity (upgrade to Starter)
- Check REDIS_HOST and REDIS_PORT env vars
- Use Internal Redis URL for services within Render

### Issue: API Health Check Failing
**Solution:**
```python
# Add health check endpoint to FastAPI app
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### Issue: Cold Starts (Free Plan)
**Solution:**
- Upgrade to Starter plan ($7/month) for always-on
- OR keep service warm with external pings:
  ```bash
  # Use cron-job.org or similar
  curl https://your-api.onrender.com/health
  ```

---

## ✅ Post-Deployment Checklist

After completing deployment:
- [ ] PostgreSQL database created and schema deployed
- [ ] Redis cache connected
- [ ] Research API responding at /health
- [ ] Telegram webhook (if used) receiving updates
- [ ] Local .env updated with Render URLs
- [ ] All environment variables set correctly
- [ ] Database backups enabled (automatic on Starter+)
- [ ] Monitoring alerts configured
- [ ] Test all API endpoints
- [ ] Verify data is persisting correctly
- [ ] Check logs for any errors

---

## 🎉 Success!

You now have:
- ✅ Production PostgreSQL with 70+ tables
- ✅ Redis caching layer
- ✅ FastAPI backend deployed
- ✅ Automatic SSL/HTTPS
- ✅ Daily automated backups
- ✅ Logs and monitoring
- ✅ Auto-deploy on git push
- ✅ 99.95% uptime SLA

### Next Steps:
1. **Deploy Frontend** (if using React/Next.js separately)
2. **Set Up Custom Domain** (optional)
3. **Configure CDN** (for static assets)
4. **Enable Monitoring** (New Relic, DataDog, etc.)
5. **Run Load Tests** (ensure performance meets needs)

### Access Your Services:
```
PostgreSQL: dpg-xxx-a.oregon-postgres.render.com:5432
Redis: red-xxx-a.oregon-redis.render.com:6379
Research API: https://ava-research-api.onrender.com
Docs: https://ava-research-api.onrender.com/docs
```

**Your AVA platform is now fully cloud-hosted! 🚀**
