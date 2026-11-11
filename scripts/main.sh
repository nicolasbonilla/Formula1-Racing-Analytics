#!/bin/bash
set -e

echo "===================================="
echo "🏎️  F1 Analytics — MAIN PIPELINE START"
echo "===================================="

# ------------------------------------------------------------
# 1. Parse arguments
# ------------------------------------------------------------
WORKSPACE=""

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        *)
            echo "❌ Unknown parameter: $1"
            echo "Usage: ./main.sh --workspace <parent-folder>"
            exit 1
            ;;
    esac
done

# ------------------------------------------------------------
# 2. Validate WORKSPACE
# ------------------------------------------------------------
if [ -z "$WORKSPACE" ]; then
    echo "❌ ERROR: WORKSPACE not provided."
    echo "Usage: ./main.sh --workspace <parent-folder>"
    exit 1
fi

WORKSPACE="${WORKSPACE%/}"

# ------------------------------------------------------------
# 3. Automatically append F1-Analytics
# ------------------------------------------------------------
PROJECT_ROOT="$WORKSPACE/Formula1-Racing-Analytics"

echo "✔ WORKSPACE (parent) = $WORKSPACE"
echo "✔ PROJECT ROOT       = $PROJECT_ROOT"
echo ""

# ------------------------------------------------------------
# 4. Validate scripts folder
# ------------------------------------------------------------
SCRIPTS="$PROJECT_ROOT/scripts"
LOG_DIR="$SCRIPTS/logs"

if [ ! -d "$SCRIPTS" ]; then
    echo "❌ ERROR: scripts folder missing at:"
    echo "   $SCRIPTS"
    exit 1
fi

# ------------------------------------------------------------
# 5. CLEAN LOGS BEFORE EXECUTION
# ------------------------------------------------------------
echo "🧹 Cleaning old logs..."
rm -rf "$LOG_DIR"
mkdir -p "$LOG_DIR"
echo "✔ Fresh logs folder created at: $LOG_DIR"
echo ""

chmod +x "$SCRIPTS"/*.sh || true

# ------------------------------------------------------------
# 6. Run orchestration
# ------------------------------------------------------------
echo "🚦 Running Orchestration..."
bash "$SCRIPTS/run_orchestration.sh" "$PROJECT_ROOT"

# ------------------------------------------------------------
# 7. Run dashboard
# ------------------------------------------------------------
echo ""
echo "🖥️  Launching Dashboard..."
bash "$SCRIPTS/run_dashboard.sh" --workspace "$PROJECT_ROOT"

# ------------------------------------------------------------
# 8. Done
# ------------------------------------------------------------
echo ""
echo "===================================="
echo "🎉 MAIN PIPELINE COMPLETED SUCCESSFULLY"
echo "===================================="
