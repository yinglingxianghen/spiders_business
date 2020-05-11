import contextlib
import time

@contextlib.contextmanager
def timeit():
    start = time.time()
    print("00000")
    yield start
    end = time.time()
    usedTime = (end - start) * 1000
    print('Use time %d ms' % usedTime)

with timeit() as f:

    print(f)

    print("1111111")

