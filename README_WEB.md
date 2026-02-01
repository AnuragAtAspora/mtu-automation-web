# 🚀 MTU Web Interface

A professional web application for automating Marketing Touch User (MTU) calculations with MoEngage and Google Sheets integration.

## ✨ Features

- **🎯 One-Click Segment Creation**: Create all 12 MTU segments in MoEngage with a single date input
- **🔗 Direct MoEngage Links**: Each segment gets a direct link to MoEngage dashboard
- **📊 MTU Calculator**: Enter segment counts and get instant MTU percentages
- **📈 Google Sheets Integration**: Automatic updates to your spreadsheet
- **📱 Mobile Friendly**: Works perfectly on phones and tablets
- **👥 Team Access**: Share URL with multiple team members
- **🎨 Professional UI**: Clean, modern Bootstrap interface

## 🌐 Live Demo

Deploy this for free on Render, Railway, or other platforms. See `deployment_guide.md` for instructions.

## 🏃‍♂️ Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Google Credentials**
   - Place `google_credentials.json` in the project root

3. **Run the App**
   ```bash
   python app.py
   ```

4. **Open Browser**
   - Go to `http://localhost:5000`

### Free Deployment (Render)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "MTU Web Interface"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repo
   - Deploy!

## 📋 User Workflow

### Step 1: Create Segments
1. Enter end date for MTU period
2. Click "Create MTU Segments"
3. Get direct links to all created segments

### Step 2: Collect Counts
1. Click links to visit MoEngage segments
2. Note down user count for each segment
3. Return to web interface

### Step 3: Calculate MTU
1. Enter all segment counts in the calculator
2. Get instant MTU percentages
3. Results automatically update Google Sheets

## 🎯 What Gets Created

**UK Segments (6):**
- All UK Users
- Active UK Users (60 days)
- UK Push Recipients
- UK Push Recipients (Active)
- UK Email Recipients  
- UK Email Recipients (Active)

**UAE Segments (6):**
- All UAE Users
- Active UAE Users (60 days)
- UAE Push Recipients
- UAE Push Recipients (Active)
- UAE Email Recipients
- UAE Email Recipients (Active)

## 📊 MTU Calculations

**Formula**: `MTU = (Active users who received communications / Total active users) × 100`

**Metrics Calculated:**
- Push MTU % (UK & UAE)
- Email MTU % (UK & UAE)
- Active user percentages
- Reach percentages
- Detailed breakdowns

## 🔧 Configuration

### MoEngage Settings
```python
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'data_center': '01'
}
```

### Google Sheets
- Sheet ID: `1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM`
- Worksheet: "MTU Metrics" (auto-created)
- Format: Vertical layout with UK/UAE columns

## 💰 Cost: $0

- ✅ **Hosting**: Free on Render/Railway
- ✅ **MoEngage APIs**: Included in subscription
- ✅ **Google Sheets API**: Free tier
- ✅ **SSL Certificate**: Included
- ✅ **Custom Domain**: Available on free plans

## 🔒 Security

- Environment variables for sensitive data
- HTTPS encryption (auto-enabled)
- Google service account authentication
- No user data stored locally

## 📱 Mobile Support

The interface is fully responsive and works great on:
- 📱 Smartphones
- 📱 Tablets  
- 💻 Desktops
- 🖥️ Large screens

## 🎨 Screenshots

### Home Page
- Clean date picker interface
- Workflow explanation
- Professional branding

### Segments Created
- List of all created segments
- Direct links to MoEngage
- Next steps guidance

### MTU Calculator
- Organized input forms
- UK/UAE side-by-side layout
- Helpful tooltips

### Results Page
- Summary cards with key metrics
- Detailed analysis table
- Actionable insights

## 🚀 Benefits Over Command Line

1. **👥 Team Access**: Anyone can use it
2. **📱 Mobile Friendly**: Works on any device
3. **🔗 Direct Links**: Jump to MoEngage segments
4. **📊 Visual Results**: Charts and formatted tables
5. **🎯 User Friendly**: No technical knowledge required
6. **🌐 Always Available**: 24/7 web access
7. **📈 Professional**: Branded, polished interface

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Font Awesome
- **APIs**: MoEngage, Google Sheets
- **Hosting**: Render/Railway (free)
- **Database**: None required (stateless)

## 📞 Support

For issues or questions:
1. Check the deployment guide
2. Verify Google credentials
3. Test MoEngage API access
4. Review browser console for errors

## 🎉 Success!

You now have a professional web interface that makes MTU automation accessible to your entire team. No more command line tools - just clean, simple web forms that anyone can use!

**Share the URL with your team and start calculating MTU percentages in minutes, not hours.**