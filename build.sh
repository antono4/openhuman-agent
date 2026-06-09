#!/bin/bash
# Build script for OpenHuman AI Agent

echo "Building OpenHuman AI Agent..."

# Install dependencies if needed
pip install pyinstaller -q 2>/dev/null

# Clean previous builds
rm -rf build dist

# Build executable
pyinstaller openhuman.spec --clean

# Create output directory
mkdir -p release

# Copy executable
cp -r dist/openhuman-agent release/

# Create README for release
cat > release/README.txt << 'EOF'
OpenHuman AI Agent
==================

Usage:
  ./openhuman-agent/agent list    - List available agents
  ./openhuman-agent/agent show <name>    - Show agent definition
  ./openhuman-agent/skill list    - List available skills
  ./openhuman-agent/skill run <name>      - Execute a skill
  ./openhuman-agent/classify "<command>" - Classify a command
  ./openhuman-agent/execute "<command>"   - Execute with security

For more information, visit: https://github.com/antono4/openhuman-agent
EOF

echo ""
echo "Build complete! Output in: release/openhuman-agent/"
ls -la release/openhuman-agent/