# 🚀 Junction Dashboard Deployment Guide
## Deploy to Hostinger VPS (69.62.78.157)

**Application:** 75% Dependable Yield Dashboard  
**Type:** React Static Site (No Backend)  
**Suggested Subdomain:** dashboard.pfepltech.com  
**VPS IP:** 69.62.78.157  

---

## 📋 WHAT WE'RE DEPLOYING

This is a simple React dashboard that:
- ✅ Shows interactive charts
- ✅ Loads data from a JSON file
- ✅ No database needed
- ✅ No backend server needed
- ✅ Just static files (HTML, CSS, JS)

---

## 🎯 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Build Your React App Locally**

Open PowerShell on your Windows machine:

```powershell
# Navigate to your dashboard
cd "C:\Users\Rutaab\Desktop\Sakina 75 percent script\junction-dashboard"

# Build for production
npm run build

# This creates a 'dist' folder with all static files
```

✅ **Verify:** You should see a `dist` folder created with `index.html`, `assets/`, etc.

---

### **STEP 2: Connect to Your VPS**

```bash
# Connect via SSH
ssh srv1006127

# Enter your password when prompted
```

---

### **STEP 3: Create Directory for Dashboard**

```bash
# Create directory
mkdir -p /var/www/junction-dashboard

# Set permissions
chmod 755 /var/www/junction-dashboard
```

---

### **STEP 4: Upload Your Built Files**

**Open a NEW PowerShell window** (keep SSH open):

```powershell
# Navigate to your project
cd "C:\Users\Rutaab\Desktop\Sakina 75 percent script\junction-dashboard"

# Upload the entire dist folder
scp -r dist/* srv1006127:/var/www/junction-dashboard/

# Wait for upload to complete
```

**Alternative: Using WinSCP**
1. Connect to VPS (srv1006127 or 69.62.78.157)
2. Navigate to `/var/www/junction-dashboard/`
3. Upload everything from your local `dist` folder

---

### **STEP 5: Verify Files on VPS**

Back in your SSH session:

```bash
# Check if files uploaded correctly
ls -la /var/www/junction-dashboard/

# You should see:
# - index.html
# - assets/ folder
# - data.json (or in public/)
```

---

### **STEP 6: Configure Nginx for Dashboard**

Create Nginx configuration:

```bash
nano /etc/nginx/sites-available/junction-dashboard
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name dashboard.pfepltech.com;

    # Dashboard files location
    root /var/www/junction-dashboard;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Serve static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|json)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # Serve the React app
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

**Save and exit:** Press `Ctrl+O`, then `Enter`, then `Ctrl+X`

---

### **STEP 7: Enable the Site**

```bash
# Create symbolic link to enable the site
ln -s /etc/nginx/sites-available/junction-dashboard /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# If test passes, restart Nginx
systemctl restart nginx

# Check Nginx status
systemctl status nginx
```

---

### **STEP 8: Configure DNS for Subdomain**

Go to your domain registrar (where you manage pfepltech.com):

**Add this DNS record:**
```
Type: A
Name: dashboard
Value: 69.62.78.157
TTL: 3600 (or Auto)
```

This creates: `dashboard.pfepltech.com` → `69.62.78.157`

⏰ **Wait 5-30 minutes** for DNS propagation.

---

### **STEP 9: Test Your Dashboard (HTTP)**

After DNS propagates, test in browser:

```
http://dashboard.pfepltech.com
```

You should see your junction dashboard! 🎉

---

### **STEP 10: Install SSL Certificate (HTTPS)**

```bash
# Install Certbot (if not already installed)
apt install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d dashboard.pfepltech.com

# Follow prompts:
# - Enter your email
# - Agree to terms (Y)
# - Choose to redirect HTTP to HTTPS (option 2)
```

---

### **STEP 11: Verify HTTPS Works**

Open browser and visit:

```
https://dashboard.pfepltech.com
```

✅ You should see:
- 🔒 Padlock icon (secure)
- Your interactive charts
- All data loading correctly

---

## 🧪 TESTING CHECKLIST

- [ ] Dashboard loads: `https://dashboard.pfepltech.com`
- [ ] HTTP redirects to HTTPS
- [ ] Both charts display correctly
- [ ] Junction selector dropdown works
- [ ] Max/Min/Average selector works
- [ ] All interactive features work (zoom, hover, etc.)
- [ ] Data loads from JSON file

---

## 🔄 HOW TO UPDATE THE DASHBOARD

When you make changes and want to update:

### **On Windows (Local):**

```powershell
cd "C:\Users\Rutaab\Desktop\Sakina 75 percent script\junction-dashboard"

# Build new version
npm run build

# Upload to VPS
scp -r dist/* srv1006127:/var/www/junction-dashboard/
```

### **On VPS:**

```bash
# Clear Nginx cache (optional)
systemctl restart nginx
```

That's it! Your dashboard will be updated instantly.

---

## 🚨 TROUBLESHOOTING

### **Dashboard not loading:**

```bash
# Check if files exist
ls -la /var/www/junction-dashboard/

# Check Nginx error logs
tail -f /var/log/nginx/error.log

# Restart Nginx
systemctl restart nginx
```

### **Charts not showing:**

```bash
# Verify data.json exists
ls -la /var/www/junction-dashboard/data.json
# OR
ls -la /var/www/junction-dashboard/assets/

# Check browser console for errors (F12)
```

### **DNS not working:**

- Check DNS propagation: https://www.whatsmydns.net/
- Type: `dashboard.pfepltech.com`
- Wait 5-30 minutes if just added

### **SSL issues:**

```bash
# Check certificate status
certbot certificates

# Renew if needed
certbot renew
```

---

## 📊 DEPLOYMENT SUMMARY

| Item | Value |
|------|-------|
| **VPS IP** | 69.62.78.157 |
| **Domain** | dashboard.pfepltech.com |
| **Location** | /var/www/junction-dashboard |
| **Web Server** | Nginx |
| **SSL** | Let's Encrypt (Certbot) |
| **Type** | Static React App |

---

## 🎯 ALTERNATIVE SUBDOMAINS

If you want a different subdomain, just change these:

**In DNS:**
- Use different name (e.g., `junctions`, `yield`, `charts`)

**In Nginx config:**
- Change `server_name` line

**Examples:**
- `junctions.pfepltech.com`
- `yield.pfepltech.com`
- `charts.pfepltech.com`
- `waterdata.pfepltech.com`

---

## ✅ QUICK COMMANDS REFERENCE

```bash
# View Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Restart Nginx
systemctl restart nginx

# Test Nginx config
nginx -t

# Check SSL certificate
certbot certificates

# Renew SSL
certbot renew

# Check files
ls -la /var/www/junction-dashboard/
```

---

## 🎉 SUCCESS!

Once completed, your dashboard will be live at:
**https://dashboard.pfepltech.com**

Anyone can access it with just the URL - no login needed!

---

**Note:** This is a static site, so it's very fast, secure, and requires minimal server resources!

