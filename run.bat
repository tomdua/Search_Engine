set python_path= "C:\Users\Tom\AppData\Local\Programs\Python\Python38-32\python.exe"

%python_path% -m pip install virtualenv
%python_path% -m venv venv

mkdir venv\nltk_data

venv\Scripts\activate & ^
python -m pip install --upgrade pip & ^
pip install -r requirements.txt & ^
python setup.py & ^
deactivate

