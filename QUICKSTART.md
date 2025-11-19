# ⚡ Quick Start Guide - Healthcare Analytics

## 🚨 READ THIS FIRST!

**Your cPanel won't work with this app** because Streamlit (the framework) needs:
- Persistent Python process (cPanel uses CGI)
- WebSocket support (not available on cPanel)
- Direct port access (limited on cPanel)

## ✅ What You Need to Do:

### Option 1: Use Cloud Hosting (EASIEST & FREE)
1. Go to **render.com** (free tier)
2. Create account → New Web Service
3. Connect GitHub repo or upload files
4. Deploy! Takes 5 minutes.

### Option 2: Get a VPS (BEST, $5/month)
1. DigitalOcean, Linode, or Vultr
2. $5/month gets you full control
3. Follow DEPLOYMENT_GUIDE.md

---

## 💻 Test Locally First (5 Minutes)

```bash
# 1. Run setup (does everything automatically)
./setup.sh

# 2. Start app
source venv/bin/activate
streamlit run app.py

# 3. Open browser
http://localhost:8501

# Login: Billingpro / Guard2026!
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| **README.md** | Full documentation & options |
| **DEPLOYMENT_GUIDE.md** | Step-by-step for each platform |
| **CHANGES.md** | What was fixed |
| **setup.sh** | Automated installation |
| **.env.example** | Configuration template |

---

## ⚙️ Configuration (Quick)

1. Copy `.env.example` to `.env`
2. Edit these lines:
```env
DB_TYPE=mysql                    # Change if using PostgreSQL
MYSQL_HOST=your-host
MYSQL_DATABASE=your-database
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
SECRET_KEY=random-string-here    # CHANGE THIS!
```

---

## 🎯 Deployment Decision Tree

```
Do you have cPanel?
├─ YES → Does it have "Setup Python App" feature?
│        ├─ YES → Try Option 4 in DEPLOYMENT_GUIDE (but NOT recommended)
│        └─ NO  → Use Render.com (free) or get VPS ($5/mo)
└─ NO  → What do you prefer?
         ├─ Free → Use Render.com or Streamlit Cloud
         ├─ Full Control → Get VPS ($5/month)
         └─ Enterprise → AWS/GCP/Azure
```

---

## 🔥 Recommended: Render.com (Free)

**Why?** Free, easy, works perfectly with Streamlit.

**How?**
1. Go to render.com → Sign up (free)
2. New → Web Service
3. Connect GitHub or upload files
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `streamlit run app.py --server.port $PORT`
5. Add environment variables from your .env
6. Deploy!

**URL:** You get a free `.onrender.com` subdomain

---

## 🆘 Problems?

### "Can't connect to database"
```bash
# Test connection
python database.py

# For MySQL, verify:
mysql -h host -u user -p database
```

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Permission denied"
```bash
chmod +x setup.sh
chmod -R 755 .
```

---

## 📖 More Info

- **Features**: See PROJECT_DOCUMENTATION.md
- **Deployment**: See DEPLOYMENT_GUIDE.md  
- **Changes**: See CHANGES.md
- **Full Docs**: See README.md

---

## 💡 TL;DR

1. **Can't use cPanel** (technical limitations)
2. **Use Render.com** (free, 5 min setup)
3. **Or get VPS** ($5/month, full control)
4. **Test locally first** (run `./setup.sh`)

**Start here:** Run `./setup.sh` to test locally, then choose deployment platform from DEPLOYMENT_GUIDE.md

Good luck! 🚀
