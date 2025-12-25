#!/usr/bin/env python3

import argparse
import os
import requests
import gnupg
import tempfile
from urllib.parse import urlparse

# ----------------------------
# Argument Parser
# ----------------------------
parser = argparse.ArgumentParser(
    description="Download and decrypt a GPG encrypted file."
)
parser.add_argument(
    "url",
    metavar="URL",
    help="URL of the encrypted file to download."
)
parser.add_argument(
    "output_path",
    metavar="OUTPUT",
    nargs="?",
    help="Optional path to save the decrypted file. Defaults to the filename inferred from URL."
)
args = parser.parse_args()

# ----------------------------
# Ensure /raw at the end of URL
# ----------------------------
url = args.url
if not url.endswith("/raw"):
    url = url.rstrip("/") + "/raw"

# ----------------------------
# Initialize GPG
# ----------------------------
gpg = gnupg.GPG()
gpg.encoding = "utf-8"

# ----------------------------
# Determine temporary path for the downloaded encrypted file
# ----------------------------
filename_encrypted = os.path.basename(urlparse(url).path)
tmp_encrypted_path = os.path.join(tempfile.gettempdir(), filename_encrypted)

# ----------------------------
# Download the encrypted file from the URL
# ----------------------------
try:
    response = requests.get(url, stream=True)
    response.raise_for_status()
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
    # Extract real filename before /raw
    path_parts = urlparse(url).path.split("/")
    if len(path_parts) >= 2:
        decrypted_filename = path_parts[-2]  # nombre real antes de /raw
    else:
        decrypted_filename = filename_encrypted
    decrypted_path = decrypted_filename

# ----------------------------
# Decrypt the file
# ----------------------------
with open(tmp_encrypted_path, "rb") as f:
    decrypted = gpg.decrypt_file(f, output=decrypted_path)
    f.seek(0)

    if decrypted.ok:
        print(f"File decrypted successfully: {decrypted_path}")
    elif decrypted.status == "no secret key":
        print("[*] Error: no secret key available to decrypt the asymmetric file")
    else:
        print("[*] The file requires a passphrase")
        passphrase = input("Enter the passphrase: ")
        decrypted = gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_path)
        if decrypted.ok:
            print(f"File decrypted successfully: {decrypted_path}")
        else:
            print(f"Error decrypting file: {decrypted.status}")
