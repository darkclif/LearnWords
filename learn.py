import sys
import os
import random
import shutil

RATE_SUB   = -0.03
RATE_ADD   = 0.06

class cl_input:
    def __init__(self, inp):
        self.arr = inp.split()

    def check(self, i, what):
        if not i < len(self.arr):
            return False
        
        return self.arr[i].lower() == what.lower()

    def check_flag(self, i, flag):
        if not i < len(self.arr):
            return False
        
        flags = self.arr[i].split()
        return (flag.lower() in flags)

    def get(self, i, default):
        return self.arr[i] if i < len(self.arr) else default

    def get_int(self, i, default):
        return int(self.arr[i]) if i < len(self.arr) else default

def get_input():
    inp = input().lower()
    return cl_input(inp)

class word:
    def __init__(self, w1, w2, rate = 0.0):
        self.words = [w1, w2]
        self.repeat = False
        self.rate = float(rate)

    def should_repeat(self):
        return self.repeat

    def change_rate(self, change):
        self.rate = min(max(self.rate + change, 0.0), 1.0) 

    def get_word(self, which, flipped = False):
        return self.words[(which + (1 if flipped else 0)) % 2]

    def __str__(self) -> str:
        return "{};{};{:.2}".format(self.words[0], self.words[1], self.rate)


def get_sorted_by_rate(words):
    # words_out = [(w, int(w.rate * 10.0)) for w in words] 
    words_out = words[:]
    # random.shuffle(words_out)
    return sorted(words_out, key= lambda x: x.rate)

def print_words(words, sorted = False):
    if sorted:
        words = get_sorted_by_rate(words)
    for w in words:
        print("{:12} --> {:12} (r: {:.4})".format(w.get_word(0), w.get_word(1), w.rate))
    input()

def learn(words_in, n, flip = False):
    words = words_in[:n]

    loop = True
    while loop:
        for w in words:
            w.repeat = False
        random.shuffle(words)

        total = len(words)
        correct = 0
        left_early = False

        words_left = words[:]

        while len(words_left) > 0:
            os.system("cls")
            print("Left: ", len(words_left))
            print("")

            curr_word : word = words_left[0]
            words_left = words_left[1:]

            print("Translate: {} (r: {:.2})".format(curr_word.get_word(0, flip), curr_word.rate))
            inp = input()

            if inp == 'q':
                left_early = True
                break

            if inp.strip() == curr_word.get_word(1, flip).strip():
                print("Correct!")
                input()
                if not curr_word.should_repeat():
                    correct += 1
            else:
                print("Wrong. Correct answer is: ", curr_word.get_word(1, flip))
                input()
                curr_word.repeat = True 
                words_left += [curr_word]

        # Calc rate
        if not left_early:
            for w in words:
                if not w.should_repeat():
                    w.change_rate(RATE_ADD)
                else:
                    w.change_rate(RATE_SUB)
            
        # Take input
        loop2 = True
        while loop2:
            loop2 = False
            
            os.system("cls")
            msg = "Canceled!" if left_early else "Finished!"
            print("{} Result: {}/{}".format(msg, correct, total))
            print("(R - repeat; F - repeat flipped; P - print all; A [n] - add words)")
            inp = get_input()

            if inp.check(0, 'a'):
                n += inp.get_int(1, 0)
                words = words_in[:n]

            elif inp.check(0, 'r'):
                pass

            elif inp.check(0, 'p'):
                print_words(words)
                loop2 = True

            elif inp.check(0, 'f'):
                flip = not flip

            else:
                loop = False

def load_words(file_name):
    words = []

    with open(file_name, 'r') as f:
        lines = f.readlines()
        lines = [l.split(";") for l in lines]
        words = [word(l[0].strip(), l[1].strip(), l[2].strip() if len(l) > 2 else 0.0) for l in lines]  

    return words

def store_words(file_name, words):
    with open(file_name, 'w') as f:
        lines = [str(w) + "\n" for w in words]
        lines[-1].strip()
        f.writelines(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Pass file name.")
        exit()

    file_name = sys.argv[1]
    bck_dest = file_name + ".bck"
    words = load_words(file_name)

    loop = True
    while loop:
        os.system("cls")
        print("L [n] [fs] - learn; P [s] - print words; E - exit; HELP - print help")
        inp = get_input()

        if inp.check(0, 'help'):
            print("[L] - Learn specific amount of words.")
            print("   (pos.arg) [n] - Number of words for learing.")
            print("   (flag:)   [f] - Flip direction of languages.")
            print("   (flag:)   [s] - Pick lowest weight first.")

            print("[P] - Print all words in current file.")
            print("   (flag:)   [s] - Sort by lowest weight first.")

            print("[SAVE] - Save words with weights into current file.")
            print("[BCK] - Make backup.")
            input()

        elif inp.check(0,'l'):
            count = inp.get_int(1, 10)      # number of words
            flip = inp.check_flag(2, 'f')   # flip direction
            s = inp.check_flag(2, 's')      # pick lowest weight first

            words_in = []
            if s:
                words_in = get_sorted_by_rate(words)
            else:
                words_in = words
                random.shuffle(words_in)

            learn(words_in, count, flip)
            store_words(file_name, words)

        elif inp.check(0,'e'):
            exit()

        elif inp.check(0, 'p'):
            s = inp.check_flag(1, 's')

            print_words(words, s)

        elif inp.check(0, 'save'):
            store_words(file_name, words)

        elif inp.check(0, 'bck'):
            shutil.copyfile(file_name, bck_dest)

        else:
            print("Unknown command.")
            input()
