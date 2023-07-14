import os
from tkinter import Tk, filedialog
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


def decrypt_aes(key, data):
    nonce = data[:16]
    ciphertext = data[16:-16]
    tag = data[-16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext


def decrypt_rsa(private_key, data):
    cipher = PKCS1_OAEP.new(private_key)
    plaintext = cipher.decrypt(data)
    return plaintext


def decrypt_xor(key, data):
    decrypted_data = bytearray()
    for byte in data:
        decrypted_data.append(byte ^ key)
    return bytes(decrypted_data)


def download_file_from_firebase(file_name, folder_name):
    bucket = storage.bucket()
    blob = bucket.blob(folder_name + "/" + file_name)
    file_content = blob.download_as_bytes()
    return file_content


# Initialize Firebase
cred = credentials.Certificate("firebasefile.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'cloud-storage-system-84be3.appspot.com'
})

# Create Tkinter root window
root = Tk()
root.withdraw()  # Hide the root window

# Select the file to download
file_name = filedialog.asksaveasfilename(defaultextension=".txt")

if file_name:
    # Folder name on Firebase
    firebase_folder_name = "encrypted_files"

    # Download segments from Firebase
    segment1_data = download_file_from_firebase("segment1.bin", firebase_folder_name)
    segment2_data = download_file_from_firebase("segment2.bin", firebase_folder_name)
    segment3_data = download_file_from_firebase("segment3.bin", firebase_folder_name)

    # Download keys from Firebase
    aes_key_data = download_file_from_firebase("aes_key.bin", firebase_folder_name)
    rsa_key_data = download_file_from_firebase("rsa_key.pem", firebase_folder_name)
    xor_key_data = download_file_from_firebase("xor_key.bin", firebase_folder_name)

    # Create a folder to store the decrypted file
    decrypted_folder_name = "decrypted_files"
    os.makedirs(decrypted_folder_name, exist_ok=True)

    # Decrypt the segments using the keys
    decrypted_segment1 = decrypt_aes(aes_key_data, segment1_data)
    decrypted_segment2 = decrypt_rsa(RSA.import_key(rsa_key_data), segment2_data)
    decrypted_segment3 = decrypt_xor(xor_key_data[0], segment3_data)

    # Concatenate the decrypted segments
    decrypted_file_content = decrypted_segment1 + decrypted_segment2 + decrypted_segment3

    # Save the decrypted file
    file_path = os.path.join(decrypted_folder_name, file_name)
    with open(file_path, 'wb') as f:
        f.write(decrypted_file_content)

    print("File downloaded and decrypted successfully!")
else:
    print("File saving cancelled.")
