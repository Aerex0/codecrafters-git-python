import sys
import os
import zlib
import hashlib


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the code below to pass the first stage
    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        options = sys.argv[2]
        SHA = sys.argv[3]
        SHA_FOLDER = SHA[:2]
        SHA = SHA[2:]
        if options == "-p":
            with open(f".git/objects/{SHA_FOLDER}/{SHA}", "rb") as f:
                compressed_text = f.read()
                text = zlib.decompress(compressed_text)
                text = text.decode("utf-8")
                size = text.split(' ')[1].split('\0')[0]
                content = text.split('\0')[1]
                # print(content) Change this to print(content, end='') to remove the new line
                sys.stdout.write(content)
    elif command == "hash-object":
        options = sys.argv[2]
        file = sys.argv[3]
        if options == "-w":
            with open(file, "r") as f:
                content = f.read()
                file_hash = hashlib.sha1(content.encode()).hexdigest()
                file_folder = file_hash[:2]
                file_name = file_hash[2:]
                os.makedirs(f".git/objects/{file_folder}", exist_ok=True)
                with open(f".git/objects/{file_folder}/{file_name}", "wb") as f:
                    f.write(zlib.compress(f"blob {len(content)}\0{content}".encode("utf-8")))
                sys.stdout.write(file_hash)

        
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
