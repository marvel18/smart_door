if ! [ -f "data/config.ini" ]; then
    cp config.ini data/config.ini
fi
streamlit run main.py