# STT-py Usage Guide

## One-click Deployment

1. Clone the repository and navigate to the project directory  
2. Download the speech recognition models  
   ```bash
   bash download.sh
   ```  
3. Run the setup script  
   ```bash
   bash setup.sh
   ```  
4. Start speech recognition  
   ```bash
   python stt.py
   ```

## Manual Deployment

1. Download the speech recognition models  
   ```bash
   bash download.sh
   ```  
2. Create and activate the conda environment  
   ```bash
   conda env create -f environment.yml
   conda activate vosk_env
   ```  
3. Run speech recognition  
   ```bash
   python stt.py
   ```