import bcrypt
import time
import os
from multiprocessing import get_context
from nltk.corpus import words

def load_shadow_file(filename):
    entries = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            user, hash_val = line.split(":", 1)
            entries.append((user, hash_val.encode()))
    return entries

def load_dictionary():
    return [w.lower() for w in words.words() if w.isalpha() and 6 <= len(w) <= 10]

def worker(dic, hash_val, q, found, start, step):
    for i in range(start, len(dic), step):
        if found.is_set():
            return

        word = dic[i]
        if bcrypt.checkpw(word.encode(), hash_val):
            print(f"Worker {start}: FOUND {word}", flush=True)
            q.put(word)
            found.set()
            return

def crack(entries, dictionary, n):
    ctx = get_context("spawn")
    results = {}

    for user, hash_val in entries:
        start_time = time.perf_counter()

        queue = ctx.Queue()
        found = ctx.Event()
        procs = []

        for i in range(n):
            p = ctx.Process(target=worker, args=(dictionary, hash_val, queue, found, i, n))
            p.start()
            procs.append(p)

        password = None

        while any(p.is_alive() for p in procs):
            if not queue.empty():
                password = queue.get()
                found.set()
                break
            time.sleep(0.01)

        if password is not None:
            for p in procs:
                if p.is_alive():
                    p.terminate()

        for p in procs:
            p.join()

        end_time = time.perf_counter()
        results[user] = (password, end_time - start_time)

    return results

if __name__ == "__main__":
    print("Loading shadow file from shadow.txt...")
    entries = load_shadow_file("shadow.txt")

    for user, hash_bytes in entries:
        hash_str = hash_bytes.decode()
        parts = hash_str.split("$")

        algorithm = parts[1]
        workfactor = parts[2]
        salt_hash = parts[3]

        salt = salt_hash[:22]
        hash_only = salt_hash[22:]

        print(f"User: {user}")
        print(f"Algorithm: {algorithm}")
        print(f"Workfactor: {workfactor}")
        print(f"Salt: {salt}")
        print(f"Hash value: {hash_only}")

    dics = load_dictionary()
    results = crack(entries, dics, 10)

    for user, (password, total_time) in results.items():
        print(f"{user}: {password} ({total_time:.2f} seconds)")