#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to handle keyboard interrupt
trap 'echo -e "${RED}\nStopped watching ${FILE}.${NC}"; exit' SIGINT

# Check if an argument was provided
if [ "$#" -ne 1 ]; then
    echo -e "${RED}Error: No file path provided.${NC}"
    echo "Usage: $0 <path_to_python_script>"
    exit 1
fi

FILE="$1"
clear -x
echo -e "${GREEN}Watching for changes in ${FILE}. Press Ctrl+C to stop...${NC}"

while true; do
  inotifywait -e modify "$FILE" 
  clear -x 
  echo -e "${GREEN}Change detected! Executing ${FILE}...${NC}"
  python "$FILE"
  echo -e "${GREEN}Execution completed.${NC}"
done
