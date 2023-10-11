from flask import Flask, request

app = Flask(__name__)

stores = [
  {
    "name": "My Store",
    "items": [
      {
        "name": "Chair",
        "price": 16.99
      }
    ]
  }
]

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/store/")
def get_stores():
  return {"stores": stores}

@app.post("/store")
def create_store():
   request_data = request.get_json()
   new_store = {"name": request_data["name"], "items": []}  

   stores.append(new_store)
   return new_store, 201

@app.post("/store/<string:name>")
def create_item(name):
   pass