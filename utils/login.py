import hashlib


def hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()


# might as well use plain text lol
def check_key(input):
    with open('key.txt', 'r') as f:
        stored_hash = f.read().strip()
    if hash_key(input) == stored_hash:
        return True
    else:
        return False