import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("microclimate-cde2b-firebase-adminsdk-sd70l-f1a817eff7.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://microclimate-cde2b-default-rtdb.europe-west1.firebasedatabase.app/"
})
