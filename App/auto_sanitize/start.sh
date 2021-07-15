DIR = "/usr/src/appdata"
if ![-d "$DIR"]; then 
    mkdir "$DIR"
fi
if ![-f "$DIR/config.ini"]; then
    cp config.ini "$DIR/"
fi
python main.py