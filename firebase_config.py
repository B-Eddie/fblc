import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase-adminsdk.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://console.firebase.google.com/u/0/project/fblc-5dca1/database/fblc-5dca1-default-rtdb/data/~2F"
})

def get_database_ref(path):
    return db.reference(path)
