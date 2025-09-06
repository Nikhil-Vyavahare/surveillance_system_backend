from appwrite.client import Client
from appwrite.services.storage import Storage
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv
import uuid
from appwrite.input_file import InputFile  # Adjust import based on your SDK version

load_dotenv()

# ---------------------------
# Appwrite setup
# ---------------------------
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))
storage = Storage(client)

# ---------------------------
# Firebase setup
# ---------------------------
# ---------------------------
# Firebase setup
# ---------------------------
import json
import firebase_admin
from firebase_admin import credentials, db
import os

firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
firebase_db_url = os.getenv("FIREBASE_DATABASE_URL")

if not firebase_admin._apps:
    if firebase_creds_json:
        try:
            creds_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(creds_dict)
            print("✅ Firebase credentials loaded from JSON env")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
    else:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if not cred_path or not os.path.isfile(cred_path):
            raise FileNotFoundError("❌ Firebase credentials not found in env vars")
        cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(cred, {"databaseURL": firebase_db_url})

firebase_db = db.reference("detections")



# ---------------------------
# Upload to Appwrite Storage
# ---------------------------
def upload_to_appwrite(file_path: str):
    file_id = str(uuid.uuid4())

    # Open file in binary mode
    with open(file_path, "rb") as f:
        appwrite_file = InputFile.from_bytes(f.read(), os.path.basename(file_path))

    result = storage.create_file(
        bucket_id=os.getenv('APPWRITE_BUCKET_ID'),
        file_id=file_id,
        file=appwrite_file
    )

    return (
        f"{os.getenv('APPWRITE_ENDPOINT')}/storage/buckets/"
        f"{os.getenv('APPWRITE_BUCKET_ID')}/files/{result['$id']}/view"
        f"?project={os.getenv('APPWRITE_PROJECT_ID')}"
    )


# ---------------------------
# Store response in Firebase
# ---------------------------
def store_response_in_firebase(response, image_url):
    ref = firebase_db.push({
        'response': response,
        'image_url': image_url,
        'timestamp': {".sv": "timestamp"}  # ✅ Realtime Database server timestamp
    })
    return ref.key

def fetch_firebase_detections():
    data = firebase_db.get()
    if not data:
        return []

    detections = []
    for key, value in data.items():
        detections.append({
            "id": key,
            "response": value.get("response", ""),
            "image_url": value.get("image_url", ""),
            "timestamp": value.get("timestamp", "")
        })
    return detections

from appwrite.services.storage import Storage

def fetch_appwrite_files():
    result = storage.list_files(bucket_id=os.getenv("APPWRITE_BUCKET_ID"))
    files = []

    for f in result["files"]:
        files.append({
            "id": f["$id"],
            "name": f["name"],
            "url": (
                f"{os.getenv('APPWRITE_ENDPOINT')}/storage/buckets/"
                f"{os.getenv('APPWRITE_BUCKET_ID')}/files/{f['$id']}/view"
                f"?project={os.getenv('APPWRITE_PROJECT_ID')}"
            )
        })
    return files
