python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

git config --global http.sslverify false
git config --global --add safe.directory /workspace