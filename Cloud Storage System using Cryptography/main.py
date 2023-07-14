import os
import tkinter as tk
from tkinter import filedialog
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


def encrypt_aes(key, data):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + ciphertext + tag


def encrypt_rsa(public_key, data):
    cipher = PKCS1_OAEP.new(public_key)
    ciphertext = cipher.encrypt(data)
    return ciphertext


def encrypt_xor(key, data):
    encrypted_data = bytearray()
    for byte in data:
        encrypted_data.append(byte ^ key)
    return bytes(encrypted_data)


def create_firebase_folder(folder_name):
    bucket = storage.bucket()
    folder_blob = bucket.blob(folder_name + "/")
    folder_blob.upload_from_string('')


def upload_file_to_firebase(file_name, file_content, folder_name):
    bucket = storage.bucket()
    blob = bucket.blob(folder_name + "/" + file_name)
    blob.upload_from_string(file_content)


# Create a folder on the system
system_folder_name = "encrypted_files"
os.makedirs(system_folder_name, exist_ok=True)

# Initialize Firebase
cred = credentials.Certificate("firebasefile.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'cloud-storage-system-84be3.appspot.com'
})

# Create Tkinter root window
root = tk.Tk()
root.withdraw()  # Hide the root window

# Open file dialog for file selection
file_path = filedialog.askopenfilename()

# Read input file content
with open(file_path, 'rb') as f:
    file_content = f.read()

# Divide file into 3 segments
segment_size = len(file_content) // 3
segment1 = file_content[:segment_size]
segment2 = file_content[segment_size:2 * segment_size]
segment3 = file_content[2 * segment_size:]

# Generate encryption keys
aes_key = os.urandom(16)  # 16 bytes for AES-128
rsa_key = RSA.generate(2048)
xor_key = os.urandom(1)  # 1 byte for XOR

# Encrypt segments using different algorithms
encrypted_segment1 = encrypt_aes(aes_key, segment1)
encrypted_segment2 = encrypt_rsa(rsa_key.publickey(), segment2)
encrypted_segment3 = encrypt_xor(xor_key[0], segment3)

# Create a folder to store keys and segments on the system
system_encrypted_folder = os.path.join(system_folder_name, "encrypted_data")
os.makedirs(system_encrypted_folder, exist_ok=True)

# Write keys and segments to separate files on the system
with open(os.path.join(system_encrypted_folder, "segment1.bin"), 'wb') as f:
    f.write(encrypted_segment1)
with open(os.path.join(system_encrypted_folder, "segment2.bin"), 'wb') as f:
    f.write(encrypted_segment2)
with open(os.path.join(system_encrypted_folder, "segment3.bin"), 'wb') as f:
    f.write(encrypted_segment3)
with open(os.path.join(system_encrypted_folder, "aes_key.bin"), 'wb') as f:
    f.write(aes_key)
with open(os.path.join(system_encrypted_folder, "rsa_key.pem"), 'wb') as f:
    f.write(rsa_key.export_key())
with open(os.path.join(system_encrypted_folder, "xor_key.bin"), 'wb') as f:
    f.write(xor_key)


# Combine encrypted segments into one file
combined_file_content = encrypted_segment1 + encrypted_segment2 + encrypted_segment3
with open(os.path.join(system_encrypted_folder, "combined_file.bin"), 'wb') as f:
    f.write(combined_file_content)

# Create a folder on Firebase
firebase_folder_name = "encrypted_files"
create_firebase_folder(firebase_folder_name)

# Upload encrypted segments to Firebase
upload_file_to_firebase("segment1.bin", encrypted_segment1, firebase_folder_name)
upload_file_to_firebase("segment2.bin", encrypted_segment2, firebase_folder_name)
upload_file_to_firebase("segment3.bin", encrypted_segment3, firebase_folder_name)

# Upload encryption keys to Firebase
upload_file_to_firebase("aes_key.bin", aes_key, firebase_folder_name)
upload_file_to_firebase("rsa_key.pem", rsa_key.export_key(), firebase_folder_name)
upload_file_to_firebase("xor_key.bin", xor_key, firebase_folder_name)

# Upload the combined file to Firebase
upload_file_to_firebase("combined_file.bin", combined_file_content, firebase_folder_name + "/files")

print("Files uploaded successfully!")
