#!/bin/bash
# Healthcare Analytics - Automated Setup Script
# This script helps you set up the application quickly

set -e  # Exit on error

echo "================================================"
echo "Healthcare Analytics - Automated Setup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check Python version
echo "Checking Python installation..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
    print_success "Python 3.11 found"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION >= 3.9" | bc -l) )); then
        PYTHON_CMD=python3
        print_success "Python $PYTHON_VERSION found (3.9+ required)"
    else
        print_error "Python 3.9 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check pip
echo ""
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 not found. Please install pip."
    exit 1
fi
print_success "pip found"

# Create virtual environment
echo ""
echo "Setting up virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "All dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Setup environment file
echo ""
echo "Setting up environment configuration..."
if [ -f ".env" ]; then
    print_warning ".env file already exists. Skipping."
else
    cp .env.example .env
    print_success ".env file created from template"
    print_warning "IMPORTANT: Edit .env file with your database credentials!"
fi

# Database type selection
echo ""
echo "================================================"
echo "Database Configuration"
echo "================================================"
echo ""
echo "Which database would you like to use?"
echo "1) MySQL (for cPanel/most web hosts)"
echo "2) PostgreSQL (for cloud hosting)"
echo "3) SQLite (for local testing only)"
echo ""
read -p "Enter your choice (1-3): " db_choice

case $db_choice in
    1)
        echo ""
        print_info "MySQL selected"
        sed -i 's/DB_TYPE=.*/DB_TYPE=mysql/' .env
        echo ""
        print_warning "You need to configure MySQL settings in .env file:"
        echo "  - MYSQL_HOST"
        echo "  - MYSQL_DATABASE"
        echo "  - MYSQL_USER"
        echo "  - MYSQL_PASSWORD"
        ;;
    2)
        echo ""
        print_info "PostgreSQL selected"
        sed -i 's/DB_TYPE=.*/DB_TYPE=postgresql/' .env
        echo ""
        print_warning "You need to set DATABASE_URL in .env file"
        ;;
    3)
        echo ""
        print_info "SQLite selected (for testing only)"
        sed -i 's/DB_TYPE=.*/DB_TYPE=sqlite/' .env
        ;;
    *)
        print_error "Invalid choice. Defaulting to SQLite."
        sed -i 's/DB_TYPE=.*/DB_TYPE=sqlite/' .env
        ;;
esac

# Test database connection
echo ""
echo "Testing database connection..."
$PYTHON_CMD database.py
if [ $? -eq 0 ]; then
    print_success "Database connection successful"
else
    print_error "Database connection failed. Please check your .env settings."
    exit 1
fi

# Initialize database
echo ""
read -p "Would you like to initialize the database now? (y/n): " init_db
if [ "$init_db" = "y" ] || [ "$init_db" = "Y" ]; then
    echo "Initializing database..."
    $PYTHON_CMD -c "from database import init_db; init_db()"
    if [ $? -eq 0 ]; then
        print_success "Database initialized successfully"
        echo ""
        print_info "Default credentials created:"
        echo "  Username: Billingpro"
        echo "  Password: Guard2026!"
        print_warning "Please change these credentials after first login!"
    else
        print_error "Database initialization failed"
    fi
fi

# Setup complete
echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
print_info "To start the application:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     streamlit run app.py"
echo ""
echo "  3. Open browser to: http://localhost:8501"
echo ""
print_warning "Before deploying to production:"
echo "  - Edit .env and change SECRET_KEY"
echo "  - Update database credentials"
echo "  - Change default user password"
echo "  - Review DEPLOYMENT_GUIDE.md"
echo ""
print_success "Setup script completed successfully!"
echo ""
