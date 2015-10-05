from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
  return "Landing page placeholder"

if __name__ == '__main__':
    app.run(port=5123)