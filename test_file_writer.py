import numpy as np
import time
import Config


PERIODICITY = 0.1  # This is in seconds
TARGET_FILE = Config.Config.get("TEST_FILE_WRITER_LOCATION")


def main():
    mean = 0
    std_dev = 1.0
    with open(TARGET_FILE, 'w') as f:
        f.truncate(0)

    while True:
        with open(TARGET_FILE, "a") as f:
            f.write(str(np.random.normal(loc=mean, scale=std_dev)) + '\n')

        time.sleep(PERIODICITY)


if __name__ == '__main__':

    main()
