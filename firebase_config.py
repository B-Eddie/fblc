import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase-adminsdk.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://.firebaseio.com/"
})

def get_database_ref(path):
    return db.reference(path)
