# STT-py Usage Guide

## One-click Deployment

1. Clone the repository and navigate to the project directory  
2. Run the setup script  
   ```bash
   bash setup.sh
   ```  
3. Start speech recognition  
   ```bash
   python stt.py
   ```

## Manual Deployment

1. Create and activate the conda environment  
   ```bash
   conda env create -f environment.yml
   conda activate vosk_env
   ```  
2. Run speech recognition  
   ```bash
   python stt.py
   ```