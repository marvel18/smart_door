if ! [ -f "data/config.ini" ]; then
    cp config.ini data/config.ini
streamlit run main.py