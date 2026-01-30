#!/bin/bash
# UniLogX Installation and Startup Script
# Run this file to set up and start UniLogX

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         UniLogX - Log Analysis Platform                                                                                                                                                                                                             ║"
echo "║                   Installation Script                                                                                                                                                                                                                                              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version

# Create virtual environment (optional)
read -p "Would you like to create a virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

# Create log directories
echo "📁 Creating log directories..."
mkdir -p Log/win/{system,security,application,setup,network}
mkdir -p Log/LinX/{syslog,auth,kernel,audit,cron,services}
echo "✅ Log directories created"

# Final message
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete - Ready to Start!                                                                                                                                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📝 To start UniLogX, run:"
echo "   python unilogx_main.py"
echo ""
echo "📊 The modern cyber-style dashboard will open automatically"
echo "   using CustomTkinter GUI"
echo ""
echo "For Linux users to collect system logs, run with sudo:"
echo "   sudo python unilogx_main.py"
echo ""
echo "📚 For more information, see README.md"
echo ""
