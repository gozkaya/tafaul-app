# TAFA'UL Backend Deployment Guide

## The Problem
Your mobile app cannot connect to `https://tafaul-random.preview.emergentagent.com` because this URL only works within Emergent's development environment. Mobile apps need a **publicly accessible backend API**.

---

## SOLUTION: Deploy Backend to Railway (Recommended)

### Why Railway?
- ✅ Easy deployment from GitHub
- ✅ Automatic HTTPS
- ✅ Free $5 monthly credit
- ✅ Auto-deploy on code changes
- ✅ Simple environment variable management

---

## Step-by-Step Deployment

### Step 1: Export Your Code to GitHub

1. **In Emergent Dashboard:**
   - Click "Save to GitHub" button
   - This exports your entire project (frontend + backend)
   - Note your GitHub repository URL

### Step 2: Sign Up for Railway

1. Go to https://railway.app
2. Sign up with your GitHub account
3. Verify your account

### Step 3: Deploy Backend

1. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your TAFA'UL repository

2. **Configure Service:**
   - Railway will auto-detect it's a Python app
   - Set root directory to `/backend`
   - Or create a `railway.json` file (see below)

3. **Add Environment Variables:**
   ```
   MONGO_URL=<your_mongodb_url>
   DB_NAME=tafaul
   ```
   
   **Important:** You'll need a MongoDB database. Options:
   - **MongoDB Atlas** (Free tier): https://www.mongodb.com/cloud/atlas/register
   - **Railway MongoDB** (Add as service): Click "New" → "Database" → "MongoDB"

4. **Configure Build:**
   Create `/backend/railway.json`:
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

5. **Deploy:**
   - Railway will automatically build and deploy
   - Wait for deployment to complete (2-5 minutes)

6. **Get Your Public URL:**
   - Click on your service
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Copy your URL (e.g., `https://tafaul-api.up.railway.app`)

### Step 4: Update Mobile App Configuration

1. **Update Frontend Environment:**
   
   In `/app/frontend/.env`, change:
   ```
   EXPO_PUBLIC_BACKEND_URL=https://your-railway-url.up.railway.app
   ```

2. **Rebuild Your App:**
   ```bash
   cd /app/frontend
   eas build --platform all
   ```

3. **Upload to TestFlight:**
   - Download the new .ipa file
   - Upload to App Store Connect
   - Submit to TestFlight

### Step 5: Test

Test your mobile app - it should now connect successfully!

---

## Alternative: MongoDB Atlas Setup (Free)

If you need MongoDB:

1. **Sign up:** https://www.mongodb.com/cloud/atlas/register
2. **Create Free Cluster:**
   - Choose "Shared" (Free)
   - Select a region close to you
   - Create cluster (takes 3-5 minutes)

3. **Configure Access:**
   - Click "Database Access" → "Add New User"
   - Username: `tafaul`
   - Password: (generate secure password)
   - Privileges: Read and write to any database
   
4. **Network Access:**
   - Click "Network Access" → "Add IP Address"
   - Select "Allow Access from Anywhere" (0.0.0.0/0)
   - Confirm

5. **Get Connection String:**
   - Click "Database" → "Connect"
   - Choose "Connect your application"
   - Copy connection string
   - Replace `<password>` with your actual password
   - Add to Railway environment variables

---

## Alternative Solutions

### Option A: Direct API Integration (No Backend)

Since your backend just proxies Al-Quran Cloud API, you could call it directly:

**Pros:**
- No backend deployment needed
- Simpler architecture
- Lower costs

**Cons:**
- Less control
- No caching
- No custom logic

**Implementation:**
Update your frontend to call `https://api.alquran.cloud` directly instead of your backend.

### Option B: Serverless Functions (Vercel/Netlify)

Deploy your backend as serverless functions:

**Vercel:**
1. Create `/backend/api/[endpoint].py` files
2. Deploy to Vercel
3. Free tier: 100GB bandwidth, 100,000 requests/month

**Netlify:**
1. Create `/backend/netlify/functions/` directory
2. Convert FastAPI to Netlify Functions
3. Free tier: 100GB bandwidth, 125,000 requests/month

---

## Cost Comparison

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| **Railway** | $5 credit/month | $5/month + usage |
| **Render** | 750 hours/month free | $7/month |
| **Fly.io** | 3 shared VMs free | $1.94/month |
| **MongoDB Atlas** | 512 MB storage free | $9/month (10GB) |
| **Vercel** | 100GB bandwidth free | $20/month |

**Recommended for TAFA'UL:**
- **Railway + MongoDB Atlas Free** = ~$5/month total

---

## Files to Add to Your Repository

### `/backend/railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `/backend/Procfile` (Alternative)
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### `/backend/.dockerignore` (Optional)
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.git/
```

---

## Testing Your Deployed Backend

Once deployed, test your API:

```bash
# Test random verse endpoint
curl https://your-railway-url.up.railway.app/api/random-verse?language=en

# Test languages endpoint
curl https://your-railway-url.up.railway.app/api/languages

# Test specific verse
curl https://your-railway-url.up.railway.app/api/verse/2/255?language=en
```

All should return JSON responses.

---

## Troubleshooting

### Issue: "Application failed to respond"
**Solution:** Check logs in Railway dashboard, ensure PORT environment variable is used.

### Issue: "Database connection failed"
**Solution:** Verify MongoDB connection string in environment variables, check IP whitelist in MongoDB Atlas.

### Issue: "Module not found"
**Solution:** Ensure `requirements.txt` is up to date:
```bash
cd /app/backend
pip freeze > requirements.txt
```

### Issue: Mobile app still can't connect
**Solution:** 
1. Check if backend URL is accessible from browser
2. Ensure you rebuilt the mobile app with new URL
3. Check app logs in Xcode/Android Studio

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Set up MongoDB Atlas (if needed)
3. ✅ Update frontend environment variable
4. ✅ Rebuild mobile app
5. ✅ Upload to TestFlight
6. ✅ Test on mobile device

---

## Support

If you need help:
- **Railway Docs:** https://docs.railway.app
- **MongoDB Atlas Docs:** https://docs.atlas.mongodb.com
- **Emergent Discord:** https://discord.gg/VzKfwCXC4A

Good luck with your deployment! 🚀
