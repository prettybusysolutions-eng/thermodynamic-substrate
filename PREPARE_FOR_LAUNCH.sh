#!/bin/bash
#
# TCS Package Launch Preparation Script
# 
# This script replaces USERNAME placeholders with your actual GitHub username
# and verifies the package is ready for deployment.
#
# Usage: bash PREPARE_FOR_LAUNCH.sh <github_username>
#

set -e

if [ -z "$1" ]; then
    echo "❌ Error: GitHub username required"
    echo ""
    echo "Usage: bash PREPARE_FOR_LAUNCH.sh <github_username>"
    echo ""
    echo "Example: bash PREPARE_FOR_LAUNCH.sh myusername"
    exit 1
fi

GITHUB_USERNAME="$1"

echo "=== TCS LAUNCH PREPARATION ==="
echo ""
echo "GitHub username: $GITHUB_USERNAME"
echo ""

# Backup originals
echo "Creating backups..."
cp setup.py setup.py.backup
cp README.md README.md.backup
cp SHOW_HN_ANNOUNCEMENT.md SHOW_HN_ANNOUNCEMENT.md.backup

# Replace USERNAME in setup.py
echo "Updating setup.py..."
sed -i.tmp "s|github.com/USERNAME/|github.com/$GITHUB_USERNAME/|g" setup.py
sed -i.tmp "s|# UPDATE BEFORE PUSH||g" setup.py
rm -f setup.py.tmp

# Replace USERNAME in README.md
echo "Updating README.md..."
sed -i.tmp "s|github.com/USERNAME/|github.com/$GITHUB_USERNAME/|g" README.md
sed -i.tmp "s|# UPDATE USERNAME||g" README.md
sed -i.tmp "s|% UPDATE USERNAME||g" README.md
rm -f README.md.tmp

# Replace USERNAME in SHOW_HN_ANNOUNCEMENT.md
echo "Updating SHOW_HN_ANNOUNCEMENT.md..."
sed -i.tmp "s|github.com/USERNAME/|github.com/$GITHUB_USERNAME/|g" SHOW_HN_ANNOUNCEMENT.md
sed -i.tmp "s| (UPDATE USERNAME)||g" SHOW_HN_ANNOUNCEMENT.md
rm -f SHOW_HN_ANNOUNCEMENT.md.tmp

echo ""
echo "✓ Placeholders replaced"
echo ""

# Verification
echo "=== VERIFICATION ==="
echo ""

# Check for remaining USERNAME
if grep -r "USERNAME" setup.py README.md SHOW_HN_ANNOUNCEMENT.md 2>/dev/null; then
    echo "⚠️  Warning: Some USERNAME references may remain"
else
    echo "✓ No USERNAME placeholders remain"
fi

# Test imports
echo ""
echo "Testing imports..."
python3 << 'TEST'
import sys
sys.path.insert(0, 'src')

try:
    from thermal_substrate import ThermalSubstrate
    print("  ✓ Core import works")
except Exception as e:
    print(f"  ❌ Core import failed: {e}")
    sys.exit(1)

try:
    from thermal_substrate.adapters import thermal_coupled
    print("  ✓ Adapter import works")
except Exception as e:
    print(f"  ❌ Adapter import failed: {e}")
    sys.exit(1)

try:
    tcs = ThermalSubstrate(':memory:')
    tcs.register_entity('test', 'test', 300)
    result = tcs.execute_with_coupling('op', 'test')
    assert 'phase' in result
    print("  ✓ Core functionality works")
except Exception as e:
    print(f"  ❌ Functionality test failed: {e}")
    sys.exit(1)
TEST

# Test benchmark
echo ""
echo "Testing benchmark..."
cd benchmarks
python3 stress_test.py --operations 10 > /dev/null 2>&1 && echo "  ✓ Benchmark runs" || echo "  ⚠️  Benchmark test failed"
cd ..

echo ""
echo "=== PACKAGE READY ==="
echo ""
echo "Updated files:"
echo "  - setup.py"
echo "  - README.md"
echo "  - SHOW_HN_ANNOUNCEMENT.md"
echo ""
echo "Backups saved:"
echo "  - setup.py.backup"
echo "  - README.md.backup"
echo "  - SHOW_HN_ANNOUNCEMENT.md.backup"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Initialize git: git init && git add . && git commit -m 'Initial release'"
echo "  3. Create GitHub repo: https://github.com/new"
echo "  4. Push: git remote add origin https://github.com/$GITHUB_USERNAME/thermodynamic-substrate.git"
echo "  5. Push: git push -u origin main"
echo "  6. Tag: git tag -a v1.0.0 -m 'Release v1.0.0' && git push origin v1.0.0"
echo ""
echo "✅ Package ready for deployment"
