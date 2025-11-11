# AutoMentor CRM

A lightweight recruiting CRM for insurance agents managing their pipeline.

## Features

- ✅ Track recruits through 5 pipeline stages
- ✅ Send automated emails and texts
- ✅ Dashboard with metrics and overdue alerts
- ✅ Offline-first PWA architecture
- ✅ Mobile-responsive design

## Tech Stack

- **Backend**: Flask 3.1.2 (Python)
- **Database**: SQLite3
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: CSS Grid/Flexbox with modern animations
- **Testing**: Playwright (E2E), Pytest (API), Python requests (load)

## Local Development

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migration to create database
python migrate.py

# Start development server
python app.py
```

Visit `http://localhost:5000`

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing documentation.

```bash
# Run all tests
./run_tests.sh

# Run specific test suites
pytest tests/test_api.py -v          # API tests
npx playwright test                  # E2E tests
python tests/load_test.py            # Load tests
```

**Current Test Status**: 7/22 Playwright tests passing (31.8%). Core functionality works; form submission timing issues being addressed.

## Deployment

See [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for Render deployment instructions.

### Quick Deploy to Render

1. Push to GitHub
2. Connect repo to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables for email

## Data Backup

**Important**: Always backup your database before redeploying!

```bash
# Backup current data
cp db.sqlite3 backup_$(date +%F).sqlite3

# Or download from Render dashboard -> Shell -> Files tab
```

## Environment Variables

- `EMAIL_USER`: Gmail address for sending emails
- `EMAIL_PASS`: Gmail app password (not regular password)
- `SECRET_KEY`: Flask secret key (auto-generated if not set)

Generate Gmail app password at: https://myaccount.google.com/apppasswords

## Data Responsibility Notice

**This application is self-contained.** All recruit information and messages entered through this tool are stored within the user's own environment (local or Render). The developer (Lauren Henze) does not collect, store, or process any user data and is not responsible for its management or retention. **Users are solely responsible for backups and security of their own information.**

## Project Structure

```
automentor_crm/
├── app.py                      # Main Flask application
├── migrate.py                  # Database migration script
├── test_server.py              # Playwright test server
├── requirements.txt            # Python dependencies
├── Procfile                    # Render/Heroku config
├── static/
│   ├── app.js                  # Frontend JavaScript
│   ├── style.css               # Main styles
│   ├── workflow.css            # Pipeline-specific styles
│   ├── forms.css               # Form styles
│   ├── animations.css          # Animation styles
│   └── sw.js                   # Service worker (PWA)
├── templates/
│   ├── base.html               # Base template
│   ├── dashboard.html          # Main dashboard
│   └── add.html                # Add recruit form
├── tests/
│   ├── test_api.py             # API unit tests (Pytest)
│   ├── crm.spec.js             # E2E tests (Playwright)
│   └── load_test.py            # Load/performance tests
└── docs/
    ├── TESTING_GUIDE.md
    ├── QUICK_TEST_REFERENCE.md
    ├── TEST_DELIVERABLES.md
    ├── API_DOCS.md
    └── DEPLOY_RENDER.md
```

## API Endpoints

See [API_DOCS.md](API_DOCS.md) for complete API documentation.

**Core Endpoints**:

- `GET /` - Dashboard
- `GET /add` - Add recruit form
- `GET /api/recruits` - List all recruits
- `POST /api/recruits` - Create recruit
- `PUT /api/recruits/:id` - Update recruit
- `DELETE /api/recruits/:id` - Delete recruit

## Contributing

This is a single-user application. For bugs or feature requests, contact the developer.

## License

Proprietary - All rights reserved. Built for Gina Ortiz.

## Support

For deployment questions, see [DEPLOY_RENDER.md](DEPLOY_RENDER.md).  
For testing questions, see [TESTING_GUIDE.md](TESTING_GUIDE.md).
