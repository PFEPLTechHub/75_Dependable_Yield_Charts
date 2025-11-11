# 📋 COMPLETE HOSTINGER VPS DEPLOYMENT GUIDE
## Tender System Deployment on Hostinger VPS

**Version:** 1.0  
**Date:** January 2025  
**Domain:** tender.pfepltech.com  
**VPS IP:** 69.62.78.157  

---

## 🎯 **OVERVIEW**

This guide will help you deploy a complete Node.js + React tender system on your Hostinger VPS with:
- ✅ Backend API (Express.js + MySQL)
- ✅ Frontend (React + Vite)
- ✅ Database (MySQL)
- ✅ Web Server (Nginx)
- ✅ SSL Certificate (HTTPS)
- ✅ Custom Domain (tender.pfepltech.com)
- ✅ Process Management (PM2)

---

## 📋 **PREREQUISITES**

- ✅ Hostinger VPS (Ubuntu 24.04 LTS)
- ✅ VPS IP: 69.62.78.157
- ✅ Domain: pfepltech.com
- ✅ SSH access to VPS
- ✅ Project files ready for upload

---

## 🚀 **STEP-BY-STEP DEPLOYMENT**

### **STEP 1: Connect to Your VPS**

```bash
# Connect via SSH
ssh root@69.62.78.157

# Enter your root password when prompted
```

---

### **STEP 2: Update System & Install Required Software**

```bash
# Update system packages
apt update && apt upgrade -y

# Install Node.js 20 (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Verify installation
node -v  # Should show v20.x.x
npm -v   # Should show npm version

# Install PM2 (Process Manager for Node.js)
npm install -g pm2

# Install Nginx (Web Server)
apt install -y nginx

# Install MySQL (if not already installed)
apt install -y mysql-server

# Start and enable services
systemctl start nginx
systemctl enable nginx
systemctl start mysql
systemctl enable mysql
```

---

### **STEP 3: Set Up MySQL Database**

```bash
# Secure MySQL installation
mysql_secure_installation
# Follow prompts: Set root password, remove anonymous users, etc.

# Login to MySQL
mysql -u root -p

# In MySQL prompt, run:
CREATE DATABASE IF NOT EXISTS u221987201_tender_system
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER 'u221987201_shayanpfepl'@'localhost' IDENTIFIED BY 'ShayanPfepl@123';
GRANT ALL PRIVILEGES ON u221987201_tender_system.* TO 'u221987201_shayanpfepl'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### **STEP 4: Create Project Directory**

```bash
# Create application directory
mkdir -p /var/www/tender-system
cd /var/www/tender-system
```

---

### **STEP 5: Upload Your Project to VPS**

**Option A: Using SCP (Recommended)**

Open a NEW PowerShell window on your Windows machine:

```powershell
# Navigate to your project
cd "C:\Users\Rutaab\Desktop\PFEPL\PFEPL\tender-system-main3_single-form-section-editable\tender-system-main"

# Upload entire project (excluding node_modules)
scp -r * root@69.62.78.157:/var/www/tender-system/

# Upload hidden files like .env (if it exists)
scp .env root@69.62.78.157:/var/www/tender-system/ 2>$null
```

**Option B: Using WinSCP (GUI Tool)**

1. Download WinSCP: https://winscp.net/eng/download.php
2. Connect with:
   - **Host**: `69.62.78.157`
   - **Username**: `root`
   - **Password**: Your root password
3. Navigate to `/var/www/tender-system/` on the right side
4. Navigate to your project folder on the left side
5. Select all files and folders (except `node_modules`)
6. Drag and drop to upload

**Option C: Using Git (If your code is on GitHub)**

```bash
# On VPS
cd /var/www/tender-system
git clone YOUR_GITHUB_REPO_URL .
```

---

### **STEP 6: Install Dependencies & Set Up Environment**

Back in your SSH session:

```bash
cd /var/www/tender-system

# Install Node.js dependencies
npm install

# Create .env file
cat > .env << 'EOF'
DB_HOST=localhost
DB_USER=u221987201_shayanpfepl
DB_PASSWORD=ShayanPfepl@123
DB_NAME=u221987201_tender_system
PORT=5175
EOF

# Set proper permissions
chmod 600 .env
```

---

### **STEP 7: Import Database Schema**

```bash
cd /var/www/tender-system

# Import database tables
mysql -u u221987201_shayanpfepl -p'ShayanPfepl@123' u221987201_tender_system < database_schema.sql

# Verify tables were created
mysql -u u221987201_shayanpfepl -p'ShayanPfepl@123' u221987201_tender_system -e "SHOW TABLES;"
```

You should see tables like: `basics_shared`, `tender_details`, `project_details`, etc.

---

### **STEP 8: Build Frontend**

```bash
cd /var/www/tender-system

# Build frontend (this creates dist/ folder)
npm run build

# Verify dist folder was created
ls -la dist/
```

---

### **STEP 9: Start Backend with PM2**

```bash
cd /var/www/tender-system

# Start backend server with PM2
pm2 start server/server.js --name tender-api

# Save PM2 configuration
pm2 save

# Enable PM2 to start on system boot
pm2 startup systemd
# Copy and run the command it outputs (it will look like: sudo env PATH=...)

# Check if backend is running
pm2 status
pm2 logs tender-api

# Test backend locally
curl http://localhost:5175/api/health
curl http://localhost:5175/api/health/db
```

Expected response: `{"ok":true,"db":true}`

---

### **STEP 10: Configure Nginx**

Create Nginx configuration:

```bash
nano /etc/nginx/sites-available/tender-system
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name 69.62.78.157 tender.pfepltech.com;

    # Frontend (React app)
    root /var/www/tender-system/tender_system/dist;
    index index.html;

    # Serve static files with correct MIME types
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # Serve frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://localhost:5175;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve uploaded files
    location /uploads {
        proxy_pass http://localhost:5175;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

**Save and exit**: Press `Ctrl+O` to save, `Ctrl+X` to exit.

Enable the site and restart Nginx:

```bash
# Enable site
ln -s /etc/nginx/sites-available/tender-system /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

---

### **STEP 11: Configure Firewall**

```bash
# Allow HTTP, HTTPS, and SSH
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS (for SSL later)

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

### **STEP 12: Set Up Custom Domain**

### **A. Add DNS Records**

Go to your domain registrar (where you bought pfepltech.com) and add:

```
Type: A
Name: tender
Value: 69.62.78.157
TTL: 3600 (or Auto)
```

**This creates**: `tender.pfepltech.com` → `69.62.78.157`

Wait 5-30 minutes for DNS propagation.

### **B. Update Frontend API URL**

```bash
cd /var/www/tender-system/tender_system

# Create production environment file with your subdomain
cat > .env.production << 'EOF'
VITE_API_URL=https://tender.pfepltech.com
EOF

# Rebuild frontend with the new URL
npm run build
```

### **C. Test Domain (Before SSL)**

Open your browser and visit:
```
http://tender.pfepltech.com
```

---

### **STEP 13: Install SSL Certificate (HTTPS)**

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate for your subdomain
certbot --nginx -d tender.pfepltech.com

# Follow prompts:
# - Enter email
# - Agree to terms (Y)
# - Choose redirect HTTP to HTTPS (option 2)
```

Now your site will be accessible via **https://tender.pfepltech.com** 🎉

---

## 🧪 **TESTING YOUR DEPLOYMENT**

### **Test URLs:**

- ✅ `https://tender.pfepltech.com` - Main application
- ✅ `http://tender.pfepltech.com` - Redirects to HTTPS
- ✅ `https://tender.pfepltech.com/api/health` - Backend health
- ✅ `https://tender.pfepltech.com/api/health/db` - Database health
- ✅ `http://69.62.78.157` - IP access (backup)

### **Expected Responses:**

```json
// /api/health
{"ok":true,"env":"server","port":5175}

// /api/health/db
{"ok":true,"db":true}
```

---

## 🔧 **MAINTENANCE COMMANDS**

### **View Logs:**
```bash
# Backend logs
pm2 logs tender-api

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### **Restart Services:**
```bash
# Restart backend
pm2 restart tender-api

# Restart Nginx
systemctl restart nginx

# Restart MySQL
systemctl restart mysql
```

### **Update Application:**
```bash
cd /var/www/tender-system
git pull
npm install
npm run build
pm2 restart tender-api
systemctl restart nginx
```

### **Check Status:**
```bash
# PM2 status
pm2 status

# Service status
systemctl status nginx
systemctl status mysql

# Check if ports are in use
netstat -tuln | grep 5175
netstat -tuln | grep 80
```

---

## 🚨 **TROUBLESHOOTING**

### **Backend not working:**
```bash
pm2 logs tender-api --lines 100
# Check for errors
```

### **Database connection issues:**
```bash
mysql -u u221987201_shayanpfepl -p'ShayanPfepl@123' u221987201_tender_system -e "SHOW TABLES;"
```

### **Nginx issues:**
```bash
nginx -t
systemctl status nginx
tail -f /var/log/nginx/error.log
```

### **Domain not working:**
- Check DNS propagation: https://www.whatsmydns.net/
- Verify DNS records in domain registrar
- Wait 5-30 minutes for DNS changes

### **SSL issues:**
```bash
# Check certificate
certbot certificates

# Renew certificate
certbot renew --dry-run
```

---

## 📊 **SYSTEM INFORMATION**

### **Server Details:**
- **OS**: Ubuntu 24.04 LTS
- **IP**: 69.62.78.157
- **Domain**: tender.pfepltech.com
- **Backend Port**: 5175
- **Frontend Port**: 80/443

### **Database Details:**
- **Host**: localhost
- **User**: u221987201_shayanpfepl
- **Database**: u221987201_tender_system
- **Password**: ShayanPfepl@123

### **Project Structure:**
```
/var/www/tender-system/
├── tender_system/           # Project files
│   ├── server/             # Backend API
│   ├── src/                # Frontend source
│   ├── dist/               # Built frontend
│   ├── package.json
│   ├── .env
│   └── database_schema.sql
```

---

## ✅ **DEPLOYMENT CHECKLIST**

- [ ] Connected to VPS via SSH
- [ ] Installed Node.js, PM2, Nginx, MySQL
- [ ] Created database and user
- [ ] Uploaded project files
- [ ] Created `.env` file
- [ ] Imported database schema
- [ ] Built frontend (`npm run build`)
- [ ] Started backend with PM2
- [ ] Configured Nginx
- [ ] Configured firewall
- [ ] Added DNS records
- [ ] Updated frontend API URL
- [ ] Installed SSL certificate
- [ ] Tested application
- [ ] Verified all URLs work

---

## 🎉 **CONGRATULATIONS!**

Your tender system is now fully deployed and accessible at:
**https://tender.pfepltech.com**

---

## 📞 **SUPPORT**

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all services are running: `pm2 status`, `systemctl status nginx`
3. Check logs for error messages
4. Ensure DNS records are correct and propagated

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Deployment Date:** [Your deployment date]  

---

*This guide was created specifically for your Hostinger VPS deployment of the Tender System.*
