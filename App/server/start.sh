modprobe bcm2835-v4l2
if ! [ -f "/usr/src/appdata/config.ini" ]; then
    cp config.ini /usr/src/appdata/config.ini
fi
streamlit run main.py