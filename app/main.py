import sys
import os
import zlib
import hashlib

from sqlalchemy import null

def get_fileandfolder(SHA: str):
    folderSHA = SHA[:2]
    fileSHA = SHA[2:]
    return folderSHA, fileSHA

def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")

def get_names(tree_bytes):
    i = 0
    names = []
    contents = tree_bytes.split('\0')[1]
    while i < len(tree_bytes):
        name = contents.split(' ')[1].split('\0')[0].decode()
        names.append(name)
        i = i + 1 + 20   # skip SHA (20 bytes)

    return names

def Blob_content():
    options = sys.argv[2]
    SHA = sys.argv[3]
    SHA_FOLDER, SHA_FILE = get_fileandfolder(SHA)
    if options == "-p":
        with open(f".git/objects/{SHA_FOLDER}/{SHA_FILE}", "rb") as f:
            compressed_text = f.read()
            text = zlib.decompress(compressed_text)
            text = text.decode("utf-8")
            size = text.split(' ')[1].split('\0')[0]
            content = text.split('\0')[1]
            # print(content) Change this to print(content, end='') to remove the new line
            sys.stdout.write(content)

def create_Blob():
    options = sys.argv[2]
    file = sys.argv[3]
    if options == "-w":
        with open(file, "r") as f:
            content = f.read()
            header_content = f"blob {len(content)}\0{content}"
            file_hash = hashlib.sha1(header_content.encode()).hexdigest()
            file_folder, file_name = get_fileandfolder(file_hash)
            os.makedirs(f".git/objects/{file_folder}", exist_ok=True)
            with open(f".git/objects/{file_folder}/{file_name}", "wb") as f:
                f.write(zlib.compress(header_content.encode("utf-8")))
            sys.stdout.write(file_hash)

def tree():
    if(len(sys.argv) == 3):
        SHA = sys.argv[2]
        SHA_FOLDER, SHA_FILE = get_fileandfolder(SHA)
        with open(f".git/objects/{SHA_FOLDER}/{SHA_FILE}", "rb") as f:
            compressed_text = f.read()
            text = zlib.decompress(compressed_text)
            text = text.decode("utf-8")
            sys.stdout.write(text)

    elif(len(sys.argv) == 4):
        flag = sys.argv[2]
        SHA = sys.argv[3]
        SHA_FOLDER, SHA_FILE = get_fileandfolder(SHA)
        if flag == "--name-only":
            with open(f".git/objects/{SHA_FOLDER}/{SHA_FILE}", "rb") as f:
                compressed_text = f.read()
                text = zlib.decompress(compressed_text)
                text = text.decode("utf-8")
                names = get_names(text)
                for name in names:
                    sys.stdout.write(name + "\n")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the code below to pass the first stage
    
    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "cat-file":
        Blob_content()
    elif command == "hash-object":
        create_Blob()
    elif command == "ls-tree":
        tree()
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
