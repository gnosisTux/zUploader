#!/usr/bin/env python3

import argparse
import os
import requests
import gnupg
import tempfile

# ----------------------------
# Argument Parser
# ----------------------------
parser = argparse.ArgumentParser(
    description="Download and decrypt a GPG encrypted file."
)

# Mandatory argument: URL of the encrypted file
parser.add_argument(
    "url",
    metavar="URL",
    help="URL of the encrypted file to download."
)

# Optional argument: path to save the decrypted file
parser.add_argument(
    "output_path",
    metavar="OUTPUT",
    nargs="?",
    help="Optional path to save the decrypted file. Defaults to the same filename in the current directory."
)

args = parser.parse_args()

# ----------------------------
# Initialize GPG
# ----------------------------
gpg = gnupg.GPG()
gpg.encoding = "utf-8"  # Ensure UTF-8 encoding

# ----------------------------
# Determine temporary path for the downloaded encrypted file
# ----------------------------
filename_encrypted = os.path.basename(args.url)
tmp_encrypted_path = os.path.join(tempfile.gettempdir(), filename_encrypted)

# ----------------------------
# Download the encrypted file from the given URL
# ----------------------------
try:
    response = requests.get(args.url, stream=True)
    response.raise_for_status()  # Raise exception on HTTP errors

    with open(tmp_encrypted_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)

    print(f"Encrypted file downloaded to: {tmp_encrypted_path}")
except requests.RequestException as e:
    print(f"Error downloading file: {e}")
    exit(1)

# ----------------------------
# Determine the output path for the decrypted file
# ----------------------------
if args.output_path:
    decrypted_path = args.output_path
else:
    decrypted_path = filename_encrypted  # Save with the same name in current directory

# ----------------------------
# Decrypt the file with error handling
# ----------------------------
with open(tmp_encrypted_path, "rb") as f:
    # Attempt decryption without providing a passphrase
    decrypted = gpg.decrypt_file(f, output=decrypted_path)
    f.seek(0)  # Reset file pointer for a possible second attempt

    if decrypted.ok:
        # Decryption succeeded without a passphrase
        print(f"File decrypted successfully: {decrypted_path}")
    elif decrypted.status == "no secret key":
        # Asymmetric file: private key not available
        print("[*] Error: no secret key available to decrypt the asymmetric file")
    else:
        # Symmetric encryption or other failure: request passphrase
        print("[*] The file requires a passphrase")
        passphrase = input("Enter the passphrase: ")

        # Retry decryption with the provided passphrase
        decrypted = gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_path)

        if decrypted.ok:
            print(f"File decrypted successfully: {decrypted_path}")
        else:
            # Decryption failed even after providing a passphrase
            print(f"Error decrypting file: {decrypted.status}")
