#!/bin/bash

# Pi Storage System - Project Setup Script
# Run this in your WSL Ubuntu environment

echo "🥧 Setting up Pi Storage System..."

# Create project directory structure
echo "📁 Creating directory structure..."
mkdir -p {data,logs,frontend,tests,docs}

# Create data directory with proper permissions
chmod 755 data logs

# Create .env file for environment variables
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Development Environment Configuration
ENV=development
LOG_LEVEL=debug

# File paths (container paths)
PI_FILE_PATH=/app/data/pi_1billion.txt
SQLITE_DB_PATH=/app/data/pi_chunks.db
BINARY_FILE_PATH=/app/data/pi_binary.dat

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Storage Configuration
CHUNK_SIZE=10000
VERIFY_EVERY=100
EOF

# Create .dockerignore for better build performance
echo "🐳 Creating .dockerignore..."
cat > .dockerignore << EOF
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.vscode
.idea
*.swp
*.swo

# Project specific
data/pi_1billion.txt
data/*.db
data/*.dat
logs/*.log
*.tmp

# Node.js (if you add frontend)
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Docker
.dockerignore
Dockerfile
docker-compose*.yml
EOF

# Create gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Data files (too large for git)
data/pi_1billion.txt
data/*.db
data/*.dat

# Logs
logs/*.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
.pytest_cache/
.tox/
htmlcov/

# Docker
.dockerignore
EOF

# Create a simple nginx config for frontend
echo "🌐 Creating nginx configuration..."
cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream api {
        server pi-api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # Serve static frontend files
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files \$uri \$uri/ /index.html;
        }

        # Proxy API requests
        location /api/ {
            proxy_pass http://api/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

# Create a simple HTML frontend placeholder
echo "🎨 Creating frontend placeholder..."
cat > frontend/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pi Storage System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .api-test { background: #f0f0f0; padding: 20px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🥧 Pi Storage System</h1>
        <p>Your Pi storage API is running!</p>
        
        <div class="api-test">
            <h3>API Endpoints:</h3>
            <ul>
                <li><a href="http://localhost:8000/docs" target="_blank">📚 API Documentation</a></li>
                <li><a href="http://localhost:8000/health" target="_blank">❤️ Health Check</a></li>
                <li><a href="http://localhost:8000/digits?start=0&length=50" target="_blank">🔢 First 50 digits</a></li>
            </ul>
        </div>
        
        <div class="api-test">
            <h3>Optional Services:</h3>
            <ul>
                <li><a href="http://localhost:8080" target="_blank">🗄️ SQLite Browser</a> (Run with: <code>docker-compose --profile debug up</code>)</li>
            </ul>
        </div>
    </div>
</body>
</html>
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > start.sh << EOF
#!/bin/bash

echo "🥧 Starting Pi Storage System..."

# Check if pi file exists
if [ ! -f "data/pi_1billion.txt" ]; then
    echo "⚠️  WARNING: data/pi_1billion.txt not found!"
    echo "   Please place your pi file in the data/ directory"
    echo "   The system will still start but won't function until the file is added"
fi

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose up --build

EOF

chmod +x start.sh

# Create stop script
cat > stop.sh << EOF
#!/bin/bash
echo "🛑 Stopping Pi Storage System..."
docker-compose down
echo "✅ Stopped successfully"
EOF

chmod +x stop.sh

# Create rebuild script
cat > rebuild.sh << EOF
#!/bin/bash
echo "🔄 Rebuilding Pi Storage System..."
docker-compose down
docker-compose build --no-cache
docker-compose up
EOF

chmod +x rebuild.sh

echo ""
echo "✅ Project setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Place your pi_1billion.txt file in the data/ directory"
echo "2. Run: ./start.sh"
echo "3. Visit: http://localhost:8000/docs for API documentation"
echo ""
echo "🔧 Useful commands:"
echo "   ./start.sh         - Start the system"
echo "   ./stop.sh          - Stop the system"
echo "   ./rebuild.sh       - Rebuild containers"
echo ""
echo "🐛 Debug mode (includes SQLite browser):"
echo "   docker-compose --profile debug up"
echo ""
echo "🌐 Frontend mode (includes nginx frontend):"
echo "   docker-compose --profile frontend up"
echo ""
echo "📁 Project structure:"
tree -L 2 . 2>/dev/null || ls -la