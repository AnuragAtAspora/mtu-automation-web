# MTU Web Interface Deployment Guide

## 🚀 Free Hosting Options

### Option 1: Render (Recommended)
**Cost: FREE**

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub/Google

2. **Deploy from GitHub**
   - Push your code to GitHub repository
   - Connect Render to your GitHub
   - Create new "Web Service"
   - Select your repository
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Environment**: Python 3

3. **Add Environment Variables**
   - `SECRET_KEY`: `mtu-automation-secret-2026`
   - Upload `google_credentials.json` as a file

4. **Deploy**
   - Click "Create Web Service"
   - Your app will be live at `https://your-app-name.onrender.com`

### Option 2: Railway
**Cost: FREE (500 hours/month)**

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy**
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys

3. **Add Environment Variables**
   - Go to Variables tab
   - Add `SECRET_KEY`: `mtu-automation-secret-2026`

### Option 3: Heroku (Free tier discontinued)
**Cost: $5/month minimum**

1. **Create Heroku Account**
   - Go to [heroku.com](https://heroku.com)
   - Create account

2. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   ```

3. **Deploy**
   ```bash
   heroku create your-mtu-app
   git push heroku main
   heroku config:set SECRET_KEY=mtu-automation-secret-2026
   ```

## 📁 Required Files for Deployment

Make sure these files are in your project:

- ✅ `app.py` - Main Flask application
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Tells hosting service how to run app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `templates/` folder with all HTML files
- ✅ `google_credentials.json` - Google Sheets credentials

## 🔧 Environment Variables

Set these on your hosting platform:

- `SECRET_KEY`: `mtu-automation-secret-2026`
- `PORT`: Usually auto-set by hosting service

## 🔒 Security Notes

1. **Google Credentials**
   - Keep `google_credentials.json` secure
   - Don't commit to public repositories
   - Upload directly to hosting service

2. **MoEngage Credentials**
   - Currently hardcoded in app.py
   - Consider moving to environment variables for production

## 🌐 Custom Domain (Optional)

Most free hosting services allow custom domains:

1. **Render**: Custom domains on free plan
2. **Railway**: Custom domains available
3. **Heroku**: Custom domains on paid plans

## 📊 Usage Limits

### Render (Free Plan)
- ✅ 750 hours/month
- ✅ Custom domains
- ✅ SSL certificates
- ❌ Sleeps after 15 minutes of inactivity

### Railway (Free Plan)
- ✅ 500 hours/month
- ✅ $5 credit monthly
- ✅ No sleep mode
- ✅ Custom domains

## 🚀 Quick Start (Render)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "MTU Web Interface"
   git remote add origin https://github.com/yourusername/mtu-automation.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to render.com
   - "New" → "Web Service"
   - Connect GitHub repo
   - Deploy!

3. **Access Your App**
   - Your app will be live at: `https://your-app-name.onrender.com`
   - Share this URL with your team

## 🔗 Features of Web Interface

### ✅ What Works
- **Create Segments**: Enter date, create all MTU segments in MoEngage
- **Direct Links**: Each segment gets a direct link to MoEngage dashboard
- **MTU Calculator**: Enter counts, get calculated percentages
- **Google Sheets**: Automatic updates to your spreadsheet
- **Responsive Design**: Works on desktop and mobile
- **Professional UI**: Clean, modern interface

### 🎯 User Flow
1. **Home Page**: Enter end date for MTU period
2. **Segments Created**: Shows all created segments with direct links
3. **MTU Calculator**: Enter segment counts from MoEngage
4. **Results**: View calculated MTU percentages and insights

## 💰 Total Cost: $0

- ✅ Render/Railway: FREE hosting
- ✅ MoEngage APIs: Included in your subscription
- ✅ Google Sheets API: FREE
- ✅ Domain (optional): ~$10/year

## 🎉 Benefits of Web Interface

1. **No Technical Skills Required**: Anyone can use the web interface
2. **Always Available**: 24/7 access from anywhere
3. **Mobile Friendly**: Works on phones and tablets
4. **Team Access**: Share URL with multiple team members
5. **Professional**: Clean, branded interface
6. **Automated**: Still handles all the complex API calls
7. **Direct Links**: Jump straight to MoEngage segments

This web interface makes your MTU automation accessible to your entire team without requiring Python knowledge!