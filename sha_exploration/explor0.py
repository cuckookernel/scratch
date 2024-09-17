from hashlib import sha256
# %%


def _main():
    # %%

    h = "test string".encode('utf8')
    seen = set()
    cnt = 0

    while h not in seen and cnt < 10000000:
        seen.add(h)
        h = sha256(h).digest()
        if cnt % 100 == 0:
            print(cnt)
        cnt += 1

    print(cnt)
    # %%
