# main.py
from grid import Grid
import time

def main():
    g = Grid()
    turn = 0
    while True:
        print(f"\n--- Turn {turn} ---")
        g.display()
        time.sleep(2)
        turn += 1
        break  # Remove this once you add movement/breeding/etc.

if __name__ == "__main__":
    main()
