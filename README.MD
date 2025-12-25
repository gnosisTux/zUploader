# zUploader Client

**zUploader Client** is a Python toolkit for uploading and downloading **PGP-encrypted** files directly from the terminal. It’s fully compatible with the [zUploader-server](https://github.com/gnosisTux/zUploader-server).

![zUploader](https://i.imgur.com/QKjQiIi.png)

## Tools Included

* **zuploader.py** – Encrypt and upload files

  * Supports **symmetric** and **asymmetric** encryption.
  * Automatically detects your public keys when using asymmetric encryption.
  * Temporarily stores files with random names before uploading.

* **zget.py** – Download and decrypt files

  * Requests the passphrase only for symmetric-encrypted files.
  * Gracefully handles missing private keys for asymmetric files.

## Requirements

* Python 3.8 or higher
* [python-gnupg](https://pypi.org/project/python-gnupg/)
* requests

Quick install:

```bash
pip install python-gnupg requests
```

## Usage

### Upload a File

**Symmetric encryption:**

```bash
python3 zuploader.py --symmetric /path/to/file
```

**Asymmetric encryption:**

```bash
python3 zuploader.py --armor youremail@example.com /path/to/file
```

If `--armor` is not specified, you will be prompted to choose from your available public keys.

### Download and Decrypt a File

```bash
python3 zget.py FILE_URL [OUTPUT_PATH]
```

* Symmetric files will prompt for the passphrase.
* If no output path is provided, the file is saved in the current directory with its original name.

## License

This project is licensed under **GPLv3**.

See the `LICENSE` file for full details.

