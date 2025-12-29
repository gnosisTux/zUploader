#!/usr/bin/env python3
import gnupg
import re
import random
import string
import requests
import argparse
import os

# ----------------------------
# Configuration / Constants
# ----------------------------
URL = "https://zup.deustux.xyz"
TMPDIR = "/tmp"

# ----------------------------
# Argument Parser
# ----------------------------
parser = argparse.ArgumentParser(
    description="Encrypt a file with GPG and upload it."
)

# Optional argument for the public key email
parser.add_argument(
    "--armor",
    metavar="EMAIL",
    help="Email associated with the public GPG key (optional)."
)

# Optional flag for symmetric encryption
parser.add_argument(
    "--symmetric",
    action="store_true",
    help="Use symmetric encryption (password will be prompted via pinentry)."
)

# Mandatory argument: path to the file
parser.add_argument(
    "file_path",
    metavar="FILE",
    help="Path to the file you want to upload."
)

args = parser.parse_args()

# ----------------------------
# Initialize GPG
# ----------------------------
gpg = gnupg.GPG(options=['--trust-model'. 'always'])
gpg.encoding = 'utf-8'

# ----------------------------
# Function: List public keys and select one
# ----------------------------
def list_public_keys():    
    public_keys = gpg.list_keys()
    email_dict = {}

    for i, key in enumerate(public_keys, 1):
        uid = key['uids'][0]  # usually one UID per key
        print(f"[{i}] {key['keyid']} {uid}")
        email = re.search(r"<(.+?)>", uid).group(1)
        email_dict[i] = email

    # Validate user selection
    while True:
        try:
            selection = int(input("[*] Select [number]: "))
            if selection in email_dict:
                return email_dict[selection]
            else:
                print("Invalid number, try again.")
        except ValueError:
            print("Enter a valid number.")

# ----------------------------
# Function: Encrypt file using GPG
# ----------------------------
def encrypt_file(filepath, email=None, symmetric=False):
    # Keep the original filename extension
    basename = os.path.basename(filepath)
    temp_filename = os.path.join(TMPDIR, f"{''.join(random.choices(string.ascii_letters + string.digits, k=9))}_{basename}")

    with open(filepath, "rb") as f:
        if symmetric:
            # Symmetric encryption, pinentry will prompt for password
            encrypted_data = gpg.encrypt_file(
                f,
                recipients=None,
                symmetric=True,
                output=temp_filename
            )
        else:
            # Asymmetric encryption
            encrypted_data = gpg.encrypt_file(
                f, recipients=[email], output=temp_filename
            )

    return temp_filename

# ----------------------------
# Function: Upload file via POST
# ----------------------------
def upload_file(filepath):
    form_url = f"{URL}/upload"

    with open(filepath, "rb") as f:
        files = {"file": f}
        response = requests.post(form_url, files=files)

    if response.status_code != 200:
        print(f"Error: status code {response.status_code}")
        return

    # Extract link from response
    link = response.text.split("Download at: ")[1]
    print(link)

# ----------------------------
# Main Script
# ----------------------------
# Check that the file exists
if not os.path.isfile(args.file_path):
    print(f"Error: the file '{args.file_path}' does not exist.")
    exit(1)

# Determine encryption method and encrypt
if args.symmetric:
    # Symmetric encryption
    encrypted_file = encrypt_file(args.file_path, symmetric=True)
else:
    # Asymmetric encryption
    if not args.armor:
        email = list_public_keys()
    else:
        email = args.armor
    encrypted_file = encrypt_file(args.file_path, email=email)

# Upload the encrypted file
upload_file(encrypted_file)
