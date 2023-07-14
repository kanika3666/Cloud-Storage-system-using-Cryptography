from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    subprocess.run(['python', 'main.py'])
    return 'File upload initiated successfully!'

@app.route('/download', methods=['GET'])
def download():
    subprocess.run(['python', 'decrypt.py'])
    return 'File download and decryption initiated successfully!'

if __name__ == '__main__':
    app.run()
