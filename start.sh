#!/bin/bash
python run_engines.py &
streamlit run Home.py --server.port=8501 --server.maxUploadSize=25
