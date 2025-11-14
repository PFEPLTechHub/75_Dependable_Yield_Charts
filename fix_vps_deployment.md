# 🔧 Fix VPS Deployment - Availability Charts Not Showing

## 🔍 THE PROBLEM

**Your current path:** `/var/www/junction-dashboard/junction-dashboard`  
**Nginx serving from:** `/var/www/junction-dashboard` (parent directory)

The built files need to be in the parent directory where Nginx is looking!

---

## ✅ SOLUTION - Run These Commands on VPS

You're already SSH'd in, so run:

```bash
# 1. Make sure you're in the source directory
cd /var/www/junction-dashboard/junction-dashboard

# 2. Build the app
npm run build

# 3. Copy built files to parent directory (where Nginx serves from)
cp -r dist/* /var/www/junction-dashboard/

# 4. Verify files are in the right place
ls -la /var/www/junction-dashboard/
# You should see: index.html, assets/, availability_charts/

# 5. Clear browser cache header for new files
# Edit Nginx to remove aggressive caching temporarily
nano /etc/nginx/sites-available/junction-dashboard
```

**In the Nginx config, find this line:**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|json)$ {
    expires 1y;  # <-- Change this to 5m temporarily
```

**Change to:**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|json|html)$ {
    expires 5m;  # 5 minutes instead of 1 year
```

**Save and exit:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# 6. Test Nginx config
nginx -t

# 7. Restart Nginx
systemctl restart nginx

# 8. Clear Nginx cache (if any)
rm -rf /var/cache/nginx/*
systemctl reload nginx
```

---

## 🧪 VERIFY IT'S WORKING

### **Check Files Exist:**

```bash
# Verify the availability charts are in the right place
ls -la /var/www/junction-dashboard/availability_charts/

# You should see:
# - Nikhop_plotly.html
# - Badlapur_plotly.html
# - etc. (23 HTML files total)

# Check main files
ls -la /var/www/junction-dashboard/ | grep index.html
ls -la /var/www/junction-dashboard/assets/
```

### **Check Nginx is Serving Correct Directory:**

```bash
# View Nginx config
cat /etc/nginx/sites-available/junction-dashboard | grep root

# Should show: root /var/www/junction-dashboard;
```

### **Check Nginx Logs for Errors:**

```bash
# Watch error logs in real-time
tail -f /var/log/nginx/error.log

# In another terminal, access the site and watch for errors
```

---

## 🌐 TEST IN BROWSER

1. **Open in INCOGNITO/Private Window:**
   ```
   https://75_dependable_yield_charts.pfepltech.com
   ```

2. **Hard Refresh:**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

3. **Check Developer Console:**
   - Press `F12`
   - Go to Console tab
   - Look for any errors (especially 404s for availability_charts files)

4. **Click "Availability Charts" Tab:**
   - Select a junction
   - Chart should load

---

## 🚨 IF STILL NOT WORKING

### **Option A: Check File Permissions**

```bash
# Set correct ownership
chown -R www-data:www-data /var/www/junction-dashboard/

# Set correct permissions
chmod -R 755 /var/www/junction-dashboard/
chmod 644 /var/www/junction-dashboard/availability_charts/*.html
```

### **Option B: Verify Nginx Process**

```bash
# Check Nginx is running
systemctl status nginx

# Restart Nginx completely
systemctl stop nginx
systemctl start nginx
```

### **Option C: Check What Nginx Actually Serves**

```bash
# Test direct file access
curl http://localhost/availability_charts/Nikhop_plotly.html

# Should return HTML content, not 404
```

---

## 📊 STRUCTURE VERIFICATION

Your VPS should have this structure:

```
/var/www/junction-dashboard/          <-- Nginx serves THIS
├── index.html                         <-- Built React app
├── assets/
│   ├── index-abc123.js
│   └── index-def456.css
├── availability_charts/               <-- NEW!
│   ├── Nikhop_plotly.html
│   ├── Badlapur_plotly.html
│   └── ... (23 total)
├── data.json
├── reduced_flows.json
└── base_flows.json

/var/www/junction-dashboard/junction-dashboard/  <-- Source code
├── src/
│   ├── App.jsx                        <-- Modified
│   └── App.css                        <-- Modified
├── public/
│   └── availability_charts/           <-- NEW charts
└── package.json
```

---

## 🎯 QUICK FIX SUMMARY

**Run this complete sequence on VPS:**

```bash
cd /var/www/junction-dashboard/junction-dashboard
npm run build
cp -r dist/* /var/www/junction-dashboard/
chown -R www-data:www-data /var/www/junction-dashboard/
systemctl restart nginx
```

Then hard refresh your browser with `Ctrl + Shift + R`

---

**Let me know what you see when you run these commands!** 🚀

