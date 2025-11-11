# Deploy to Render - Configuration Guide

## Setup Overview

- **Who Owns What**: You host the app code; Gina owns her data
- **Data Storage**: SQLite database stored in `/opt/render/project/src/db.sqlite3` on Render
- **Email Credentials**: Gina configures her own Gmail app password in Render environment variables

## Render Configuration

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn app:app
```

### Environment Variables (Gina will set these)

```
EMAIL_USER=gina.ortiz.sfg@gmail.com
EMAIL_PASS=<her-gmail-app-password>
```

**Note**: Gina generates her Gmail app password herself at https://myaccount.google.com/apppasswords

## Data Persistence

### Important Notes

- Render persists SQLite files across restarts
- **Database is NOT persisted across redeploys**
- Gina must backup and re-upload `db.sqlite3` after redeployment

### Backup Instructions (for Gina)

Add to README for end user:

```bash
# Backup current data
cp db.sqlite3 backup_$(date +%F).sqlite3

# Download from Render dashboard -> Shell -> Files tab
```

She can store backups on Google Drive or her computer.

## Data Responsibility Notice

**Important**: Add this to your README:

> **Data Responsibility Notice:**  
> This application is self-contained. All recruit information and messages entered through this tool are stored within the user's own Render environment. The developer (Lauren Henze) does not collect, store, or process any user data and is not responsible for its management or retention. Users are solely responsible for backups and security of their own information.

## Deployment Steps

1. **Push Code to GitHub**

   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Create Render Web Service**

   - Go to [render.com/dashboard](https://render.com/dashboard)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: automentor-crm
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Plan**: Free

3. **Set Environment Variables** (Gina does this)

   - In Render dashboard → Environment
   - Add `EMAIL_USER` and `EMAIL_PASS`

4. **Deploy**
   - Render will automatically deploy on push to main branch
   - First deploy takes ~5-10 minutes

## Troubleshooting

### Database Not Found

- Render creates `db.sqlite3` on first run via Flask's `get_db()` function
- If issues occur, check logs: Render Dashboard → Logs

### Email Not Sending

- Verify `EMAIL_USER` and `EMAIL_PASS` are set correctly
- Ensure Gmail app password (not regular password) is used
- Check Less Secure Apps setting (though app passwords bypass this)

## Production vs Development

### Differences

- **Development**: Uses `python app.py` with Flask's built-in server
- **Production**: Uses `gunicorn app:app` for proper WSGI serving
- **Database**: Same SQLite, but in Render's filesystem

### Security Notes

- `SECRET_KEY` should be set in environment variables for production
- Current default is `'dev-key-change-in-production'`
- Recommend adding: `SECRET_KEY=<random-32-char-string>`

## Post-Deployment

### First-Time Setup

1. Navigate to deployed URL (e.g., `https://automentor-crm.onrender.com`)
2. Add initial recruits through the UI
3. Test email functionality
4. Bookmark the URL

### Regular Maintenance

- **Backups**: Download `db.sqlite3` regularly
- **Updates**: Push to GitHub → Render auto-redeploys
- **Monitoring**: Check Render logs for errors

## Support

For deployment issues:

- **Render Docs**: https://render.com/docs
- **Gunicorn Docs**: https://docs.gunicorn.org/

For application issues:

- Check Flask logs in Render dashboard
- Review error messages in browser console (F12)
