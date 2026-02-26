import sys
import os
import zlib


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
                size = text.split(b' ')[1].split(b'\0')[0]
                content = text.split(b' ')[1].split(b'\0')[1]
                print(content)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
