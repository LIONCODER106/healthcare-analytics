# Deployment Guide for Healthcare Analytics System

## ⚠️ IMPORTANT: cPanel Limitations

**Streamlit applications are NOT compatible with standard cPanel shared hosting** due to:
- Requires persistent Python process (cPanel uses CGI/WSGI)
- Needs WebSocket support for real-time updates
- Requires specific port access
- Memory and process limitations on shared hosting

## ✅ Recommended Deployment Options

### Option 1: VPS/Cloud Hosting (RECOMMENDED) ⭐

**Best For**: Production use, reliability, scalability

**Platforms**: DigitalOcean, Linode, AWS EC2, Google Cloud, Azure

**Steps**:

1. **Get a VPS**
   - Minimum: 2GB RAM, 1 CPU, 25GB storage
   - Ubuntu 22.04 or 24.04 recommended

2. **Initial Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python 3.11
   sudo apt install python3.11 python3.11-venv python3-pip -y
   
   # Install MySQL (or PostgreSQL)
   sudo apt install mysql-server -y
   ```

3. **Upload Your Application**
   ```bash
   # On your local machine
   scp -r healthcare-app-fixed username@your-server-ip:/home/username/
   
   # Or use git
   git clone https://github.com/yourusername/healthcare-app.git
   ```

4. **Setup Application**
   ```bash
   cd healthcare-app-fixed
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment file
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

5. **Configure Database**
   ```bash
   # For MySQL
   sudo mysql
   
   CREATE DATABASE healthcare_db;
   CREATE USER 'healthcare_user'@'localhost' IDENTIFIED BY 'strong_password';
   GRANT ALL PRIVILEGES ON healthcare_db.* TO 'healthcare_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

6. **Test Application**
   ```bash
   python -m streamlit run app.py --server.port 8501
   ```

7. **Setup as System Service**
   ```bash
   sudo nano /etc/systemd/system/healthcare.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Healthcare Analytics App
   After=network.target
   
   [Service]
   Type=simple
   User=username
   WorkingDirectory=/home/username/healthcare-app-fixed
   Environment="PATH=/home/username/healthcare-app-fixed/venv/bin"
   ExecStart=/home/username/healthcare-app-fixed/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable healthcare
   sudo systemctl start healthcare
   ```

8. **Setup Nginx Reverse Proxy**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/healthcare
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```
   
   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/healthcare /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **Setup SSL (Optional but Recommended)**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d yourdomain.com
   ```

---

### Option 2: Docker Deployment 🐳

**Best For**: Easy deployment, portability

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       default-libmysqlclient-dev \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements and install
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY . .
   
   # Expose port
   EXPOSE 8501
   
   # Run application
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     app:
       build: .
       ports:
         - "8501:8501"
       environment:
         - DB_TYPE=mysql
         - MYSQL_HOST=db
         - MYSQL_PORT=3306
         - MYSQL_DATABASE=healthcare_db
         - MYSQL_USER=healthcare_user
         - MYSQL_PASSWORD=secure_password
       depends_on:
         - db
       restart: always
     
     db:
       image: mysql:8.0
       environment:
         MYSQL_ROOT_PASSWORD: root_password
         MYSQL_DATABASE: healthcare_db
         MYSQL_USER: healthcare_user
         MYSQL_PASSWORD: secure_password
       volumes:
         - mysql_data:/var/lib/mysql
       restart: always
   
   volumes:
     mysql_data:
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

---

### Option 3: Cloud Platforms (EASIEST) ☁️

#### Render.com (Free tier available)
1. Connect GitHub repository
2. Select "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port $PORT`
5. Add environment variables from .env.example

#### Heroku
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0" > Procfile

# Create setup.sh
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
EOF

# Deploy
heroku create your-healthcare-app
heroku addons:create heroku-postgresql:mini
git push heroku main
```

#### Streamlit Cloud (Simplest for Streamlit apps)
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Deploy with one click

---

### Option 4: cPanel with Python App (WORKAROUND)

⚠️ **This is LIMITED and NOT recommended** but possible on some modern cPanel hosts:

**Requirements**:
- cPanel with Python app support (not all hosts have this)
- SSH access
- At least Python 3.9

**Steps**:

1. **Check if cPanel supports Python apps**
   - Login to cPanel
   - Look for "Setup Python App" under Software section
   - If not available, contact your host or use Option 1

2. **Create Python Application**
   - Click "Setup Python App"
   - Python Version: 3.11 (or highest available)
   - Application Root: `/home/username/healthcare-app`
   - Application URL: `/healthcare` or subdomain
   - Click Create

3. **Upload Files via SSH**
   ```bash
   ssh username@yourhost.com
   cd ~/healthcare-app
   
   # Upload your files here
   ```

4. **Install Dependencies**
   ```bash
   source /home/username/virtualenv/healthcare-app/3.11/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure Database**
   - Use cPanel's MySQL Database tool
   - Create database and user
   - Update .env file

6. **Modify passenger_wsgi.py** (cPanel specific)
   ```python
   import sys
   import os
   
   # Add application to path
   sys.path.insert(0, os.path.dirname(__file__))
   
   # This won't work well for Streamlit!
   # You'll need to create a Flask wrapper
   ```

**⚠️ Major Limitations**:
- No WebSocket support (breaks Streamlit's real-time features)
- Process limitations
- Poor performance
- Frequent disconnections

---

## 🔧 Configuration Steps (All Options)

### 1. Environment Variables

Copy and edit `.env` file:
```bash
cp .env.example .env
nano .env
```

Update these critical values:
- `DB_TYPE` (mysql, postgresql, or sqlite)
- `MYSQL_*` variables (if using MySQL)
- `SECRET_KEY` (generate random string)
- `MYSQL_PASSWORD` (strong password)

### 2. Initialize Database

```bash
python database.py  # Test connection
python -c "from database import init_db; init_db()"  # Create tables
```

### 3. Test Application

```bash
streamlit run app.py
```

Visit: `http://localhost:8501`

Default login:
- Username: `Billingpro`
- Password: `Guard2026!`

---

## 🔒 Security Checklist

Before going to production:

- [ ] Change `SECRET_KEY` in .env
- [ ] Use strong database passwords
- [ ] Change default user password in app
- [ ] Enable HTTPS/SSL
- [ ] Setup firewall (UFW on Linux)
- [ ] Regular database backups
- [ ] Limit database user permissions
- [ ] Keep dependencies updated
- [ ] Monitor application logs
- [ ] Setup proper file permissions

---

## 📊 Performance Optimization

1. **Database Indexing**
   - Already configured in models
   - Consider additional indexes for large datasets

2. **Caching**
   - Streamlit caching is enabled
   - Configure `CACHE_TTL_SECONDS` in .env

3. **File Upload Limits**
   - Adjust `MAX_UPLOAD_SIZE_MB` based on your needs
   - Consider splitting large files

4. **Server Resources**
   - Minimum: 2GB RAM for 10-20 concurrent users
   - Recommended: 4GB RAM for 50+ concurrent users

---

## 🆘 Troubleshooting

### "Database connection failed"
- Check database credentials in .env
- Verify database server is running
- Test connection: `mysql -u username -p`

### "Module not found"
- Activate virtual environment
- Reinstall: `pip install -r requirements.txt`

### "Port already in use"
- Change PORT in .env
- Kill existing process: `pkill -f streamlit`

### "Permission denied"
- Check file permissions: `chmod -R 755 healthcare-app-fixed`
- Check database user permissions

---

## 🎯 Recommended: VPS Hosting Providers

**Budget-Friendly**:
- DigitalOcean ($6/month droplet)
- Linode ($5/month nanode)
- Vultr ($6/month instance)

**Enterprise**:
- AWS EC2 (pay as you go)
- Google Cloud Platform
- Microsoft Azure

**Managed**:
- Render.com (free tier available)
- Heroku (free tier deprecated, paid from $7/month)
- Streamlit Cloud (free for public apps)

---

## 📝 Summary

| Option | Difficulty | Cost | Best For |
|--------|-----------|------|----------|
| VPS | Medium | $5-10/mo | Production |
| Docker | Medium | Varies | Portability |
| Cloud Platforms | Easy | Free-$10/mo | Quick start |
| cPanel | Hard | $5/mo | Last resort |

**Recommendation**: Use **VPS with Docker** or **Render.com** for best results.

---

## 📞 Next Steps

1. Choose your deployment option
2. Follow the setup guide for that option
3. Configure your .env file
4. Initialize the database
5. Test thoroughly before production
6. Setup backups and monitoring

Need help? Check the main PROJECT_DOCUMENTATION.md file for application usage instructions.
