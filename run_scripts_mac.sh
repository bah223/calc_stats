#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to display the menu
show_menu() {
    clear
    echo "================================================================================"
    echo "                            SCRIPTS LAUNCHER (macOS)"
    echo "================================================================================"
    echo ""
    echo "1 - angelina_report.py"
    echo "   Standard report generation"
    echo ""
    echo "2 - calc_stats.py"
    echo "   Quick statistics calculation from Transaction-*.xlsx files"
    echo ""
    echo "3 - 12oo.py"
    echo "   Alternative statistics calculation"
    echo ""
    echo "4 - mosteh.py"
    echo "   Report generation for a specific date range"
    echo ""
    echo "5 - rep0000.py"
    echo "   Interactive analysis with manual input for 5 merchant accounts"
    echo ""
    echo "================================================================================"
    echo ""
}

# Main loop
show_menu
read -p "Enter choice 1-5: " choice

case $choice in
    1)
        echo "Running angelina_report.py ..."
        python3 "$SCRIPT_DIR/angelina_report.py"
        ;;
    2)
        echo "Running calc_stats.py ..."
        python3 "$SCRIPT_DIR/calc_stats.py"
        ;;
    3)
        echo "Running 12oo.py ..."
        python3 "$SCRIPT_DIR/12oo.py"
        ;;
    4)
        echo ""
        read -p "Enter start date (YYYY-MM-DD): " start
        read -p "Enter end date (YYYY-MM-DD): " end
        if [ -z "$start" ] || [ -z "$end" ]; then
            echo "Error: Both dates are required!"
        else
            echo "Generating report for $start - $end..."
            python3 "$SCRIPT_DIR/mosteh.py" --start_date "$start" --end_date "$end"
        fi
        ;;
    5)
        echo "Running rep0000.py ..."
        python3 "$SCRIPT_DIR/rep0000.py"
        ;;
    *)
        echo "Invalid choice: $choice"
        ;;
esac

echo ""
echo "Script finished. Window will close in 10 seconds or press Ctrl+C to abort..."
sleep 10
