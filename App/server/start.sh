modprobe v4l2_common
if ! [ -f "/usr/src/appdata/config.ini" ]; then
    cp config.ini /usr/src/appdata/config.ini
fi
streamlit run main.py