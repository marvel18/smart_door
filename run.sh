sed  -i.bak 's/= ON/= OFF/g' config.ini && rm config.ini.bak
python3 -m streamlit run app.py
