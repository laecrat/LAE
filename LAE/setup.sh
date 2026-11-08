#!/bin/bash
# Setup script for LAE AI Assistant

echo "Setting up LAE AI Assistant..."

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create local git repository if not already
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: LAE AI Assistant"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To create a GitHub repository, run:"
echo "  1. Create a new repo at https://github.com/new"
echo "  2. Then run:"
echo "     git remote add origin https://github.com/YOUR_USERNAME/lae.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "Or use GitHub CLI:"
echo "  gh repo create lae --public --source=. --remote=origin"
echo "  git push -u origin main"