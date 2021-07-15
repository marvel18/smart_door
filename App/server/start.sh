DIR="/usr/src/appdata"
if ! [ -d "$DIR" ]; then 
    mkdir "$DIR"
    echo "directory created  $DIR"
fi
if ! [ -d "$DIR/dataset" ]; then 
    mkdir "$DIR/dataset"
    echo "directory created  $DIR/dataset"
fi
if ! [ -f "$DIR/config.ini" ]; then
    cp config.ini "$DIR/"
fi
streamlit run main.py