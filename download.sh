#!/bin/bash

# Create directory if it doesn't exist
mkdir -p model-en

# Function to download and extract model
download_model() {
    local model_name=$1
    local url="https://alphacephei.com/vosk/models/${model_name}.zip"
    
    echo "Downloading ${model_name}..."
    wget -c --no-verbose $url -P ./downloads/ || { echo "Failed to download ${model_name}"; return 1; }
    
    echo "Extracting ${model_name}..."
    unzip -o ./downloads/${model_name}.zip -d ./model-en/ || { echo "Failed to extract ${model_name}"; return 1; }
    
    echo "${model_name} successfully installed!"
    return 0
}

# Create downloads directory
mkdir -p downloads

# Download and extract all models
echo "Starting download of voice models..."

# US English models
echo "Processing US English models..."
download_model "vosk-model-small-en-us-0.15"
download_model "vosk-model-en-us-0.22"

# Indian English models
echo "Processing Indian English models..."
download_model "vosk-model-small-en-in-0.4"
download_model "vosk-model-en-in-0.5"

echo "All models have been downloaded and extracted to ./model-en/"
echo "You can now use these models with your speech recognition application."
