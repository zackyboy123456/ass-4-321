import bcrypt
import time
from multiprocessing import get_context
from nltk.corpus import words

def load_shadow_file(filename):
    entries = []
    with open(filename, "r") as f:
        for line in f:
            user, hash_val = line.strip().split(":")
            entries.append((user, hash_val.encode()))
    return entries

def load_dictionary():
    return [w.lower() for w in words.words() if w.isalpha() and 6 <= len(w) <= 10]

def worker(dic, hash_val, q, start, step):
    for i in range(start, len(dic), step):
        word = dic[i]
        if bcrypt.checkpw(word.encode(), hash_val):
            q.put(word)
            return
    q.put(None)

def crack(entries, dictionary,n):
    ctx = get_context("spawn")
    results = {}

    for user, hash_val in entries:
        start_time = time.time()

        queue = ctx.Queue()
        found = ctx.Event()
        procs = []

        # start processes
        for i in range(n):
            p = ctx.Process(target=worker, args=(dictionary, hash_val, queue, i, n))
            p.start()
            procs.append(p)

        password = None
        for x in procs:
            result = queue.get()
            if result:
                password = result
                found.set()
                break

        # wait for all processes to finish
        for p in procs:
            p.join()

        end_time = time.time()
        results[user] = (password, end_time - start_time)

    return results

if __name__ == "__main__":
    print("Loading shadow file from shadow,txt...")
    entries = load_shadow_file("shadow.txt")

    for user, hash_bytes in entries:
        hash_str = hash_bytes.decode()

        parts = hash_str.split("$")
        algorithm = parts[1]
        workfactor = parts[2]
        salt_hash = parts[3]

        salt = salt_hash[:22]
        hash_only = salt_hash[22:]

        print("User:" + str(user))
        print(f"Algorithm: " + str(algorithm))
        print(f"Workfactor: " + str(workfactor))
        print(f"Salt:" + str(salt))
        print(f"Hash value: " + str(hash_only))

    dics = load_dictionary()

    results = crack(entries, dics,4)

    for user, (password, total_time) in results.items():
        print(f"{user}: {password} ({total_time:.2f} seconds)")