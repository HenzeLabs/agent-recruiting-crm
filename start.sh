#!/bin/bash

# AutoMentor CRM - Quick Start Script

echo "🚀 Setting up AutoMentor CRM..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
python3 setup_production.py
python3 enhance_workflow.py

# Run tests
echo "🧪 Running tests..."
npm test

echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  python app.py"
echo ""
echo "To start production server:"
echo "  gunicorn --bind 0.0.0.0:5000 app:app"
echo ""
echo "🎯 Success Criteria:"
echo "  ✓ App loads in < 2s"
echo "  ✓ Stage changes apply instantly (< 200ms)"
echo "  ✓ No data loss after closing tab"
echo "  ✓ Smooth operation with 100+ records"
echo "  ✓ Works offline with local storage"