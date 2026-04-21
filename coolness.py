import random
import string
import hashlib
import time
import pandas as pd
import matplotlib.pyplot as plt


def sha256_hash(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()


def truncate_hash(hash_string, bits):
    trunchash = hash_string[:bits // 4]
    inttru = int(trunchash, 16)
    mask = (1 << bits) - 1
    return hex(inttru & mask)[2:]


def hamming_distance(s1, s2):
    count = 0
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            count += 1
    return count


def find_hamming_distance_1():
    base = ''.join(random.choice(string.ascii_letters) for _ in range(10))

    for i in range(len(base)):
        modified = list(base)
        modified[i] = chr(ord(modified[i]) ^ 1)
        modified = ''.join(modified)

        if hamming_distance(base, modified) == 1:
            return base, modified

    return None, None


def find_collision(bits, max_attempts):
    seen = {}
    start = time.time_ns()

    for i in range(max_attempts):
        s = ''.join(random.choice(string.ascii_letters) for x in range(10))
        h = truncate_hash(sha256_hash(s), bits)

        if h in seen:
            end = time.time_ns()
            return seen[h], s, i + 1, end - start
        else:
            seen[h] = s

    end = time.time_ns()
    return None, None, max_attempts, end - start

if __name__ == '__main__':
    #task 1a
    print("Task 1a: SHA256 hashes of arbitrary inputs")
    for x in  ["Hello, World!", "Python", "Cryptography"]:
        print("\n" + x)
        print(sha256_hash(x))
    # task 1b
    print("\nTask 1b: Strings with Hamming distance of 1")
    for i in range(1,4):
        out = find_hamming_distance_1()
        print("\nString 1: " + out[0])
        print("String 2: " + out[1])
        print("SHA256 (1): " + sha256_hash(out[0]))
        print("SHA256 (2): " + sha256_hash(out[1]))
    # task 1c
    print("Task 1c: Finding collisions for truncated hashes\n")
    bit = []
    times = []
    inputs = []
    hash = []
    attempts = []
    for x in range(8,51,2):
        s1,s2,y,t = find_collision(x,1000000000000000000000000)

        if s1:
            bit.append(x)
            hash.append(truncate_hash(sha256_hash(s1),x))
            times.append(t)
            attempts.append(y)
            inputs.append((s1,s2))
            print("done bit: " + str(x))
        else:
            print("timeout " + str(x))

    df = pd.DataFrame({'bits': bit, 'inputs': inputs,'hash': hash ,'attempts': attempts,'time': times})
    print(df)

    plt.plot(bit, times)
    plt.xlabel("Bits")
    plt.ylabel("Time")
    plt.title("Bits vs Time")
    plt.show()

    plt.plot(bit, attempts)
    plt.xlabel("Bits")
    plt.ylabel("Attempts")
    plt.title("Bits vs Attempts")
    plt.show()