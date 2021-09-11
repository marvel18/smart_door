modprobe v4l2_common
if ! [ -f "/data/config.ini" ]; then
    cp config.ini /usr/src/appdata/config.ini
fi
if ! [ -d "/data/dataset" ]; then
    mkdir /data/dataset
fi
streamlit run main.py