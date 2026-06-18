from itertools import chain
from pathlib import Path
import sys
import os
import random
import shutil
from typing import Any, Dict, List

RATE_SUB   = -0.03
RATE_ADD   = 0.06

############################################ INPUT
class cl_input:
    def __init__(self, inp: str):
        self.arr: List[str] = inp.split()

    def get(self, idx: int = 0):
        return (self.arr[idx] if idx < len(self.arr) else "")

    def check(self, i: int, what: str):
        if not i < len(self.arr):
            return False
        return self.arr[i].lower() == what.lower()

    def check_flag(self, i: int, flag: str):
        if not i < len(self.arr):
            return False
        return (flag.lower() in self.arr[i])

    def get_int(self, i: int, default: int):
        return (int(self.arr[i]) if (i < len(self.arr)) and (self.arr[i].isdigit()) else default)

############################################ STD CONSOLE
class SysConsole:
    def print(self, *arg: Any, **kwargs: Any) -> None:
        print(*arg, **kwargs)

    def cls(self):
        if sys.platform.startswith("win"):
            os.system("cls")
        else:
            os.system("clear")

    def get_input_ch(self) -> cl_input:
        def getch():
            if sys.platform.startswith("win"):
                import msvcrt
                return msvcrt.getch().decode("utf-8", errors="ignore")
            else:
                import tty
                import termios
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                return ch
            
        inp = getch()
        return cl_input(str(inp))

    def get_input(self) -> cl_input:
        inp = input().lower()
        return cl_input(inp)
    
    def exit(self):
        pass
console = SysConsole()

############################################ WORDS
class Word:
    def __init__(self, w1: str, w2: str, rate: str = '0.0'):
        self.words: List[str] = [w1, w2]
        self.repeat = False
        self.rate: float = float(rate) 

    def should_repeat(self):
        return self.repeat

    def change_rate(self, change: float):
        self.rate = min(max(self.rate + change, 0.0), 1.0) 

    def get_word(self, which: int, flipped: bool = False) -> str:
        return self.words[(which + (1 if flipped else 0)) % 2]

    def __str__(self) -> str:
        return "{};{};{:.2}".format(self.words[0], self.words[1], self.rate)
    
    @staticmethod
    def get_avg_rate(words: List['Word']):
        return sum([w.rate for w in words]) / len(words)

def get_sorted_by_rate(words: List[Word]) -> List[Word]:
    words_out = words[:]
    return sorted(words_out, key= lambda x: x.rate)

def print_words(words: List[Word], sorted: bool = False):
    if sorted:
        words = get_sorted_by_rate(words)
    for w in words:
        console.print("{:12} --> {:12} (r: {:.4})".format(w.get_word(0), w.get_word(1), w.rate))
    console.get_input()

def load_words(file_name: str):
    words = []
    with open(file_name, 'r', encoding="UTF-8") as f:
        lines = f.readlines()
        lines = [l.split(";") for l in lines]
        words = [Word(*l) for l in lines]  
    return words

def store_words(file_name: str, words: List[Word]):
    with open(file_name, 'w', encoding="UTF-8") as f:
        lines = [str(w) + "\n" for w in words]
        lines[-1].strip()
        f.writelines(lines)

############################################ UI
def learn_loop(words_in: List[Word], n: int, flip: bool = False):
    ''' Start single learn session. '''
    words = words_in[:n]

    loop = True
    while loop:
        for w in words:
            w.repeat = False
        random.shuffle(words)

        total: int = len(words)
        correct: int = 0
        left_early: bool = False
        words_left = words[:]

        # Guess all words until empty
        while len(words_left) > 0:
            console.cls()
            console.print(f"Left: {len(words_left)}\n")

            curr_word : Word = words_left[0]
            words_left = words_left[1:]

            console.print("Translate: {} (r: {:.2})".format(curr_word.get_word(0, flip), curr_word.rate))
            inp = console.get_input()

            if inp.check(0, 'q'):
                left_early = True
                break
            if inp.get() == curr_word.get_word(1, flip).strip():
                console.print("Correct!")
                console.get_input()
                if not curr_word.should_repeat():
                    correct += 1
            else:
                console.print("Wrong. Correct answer is: ", curr_word.get_word(1, flip))
                console.get_input()
                curr_word.repeat = True 
                words_left += [curr_word]

        # Calc new rates
        if not left_early:
            for w in words:
                if not w.should_repeat():
                    w.change_rate(RATE_ADD)
                else:
                    w.change_rate(RATE_SUB)
            
        # Decide what now
        loop2 = True
        while loop2:
            loop2 = False

            console.cls()
            msg = "Canceled!" if left_early else "Finished!"
            console.print("{} Result: {}/{}".format(msg, correct, total))
            console.print("[R - repeat; F - repeat flipped; P - print all; A [n] - add words]")
            console.print("------------------------------------------------------------------")

            # Actions
            inp = console.get_input()
            if inp.check(0, 'a'): # Add more words and repeat
                n += inp.get_int(1, 0)
                words = words_in[:n]
            elif inp.check(0, 'r'): # Repeat
                pass
            elif inp.check(0, 'p'): # Print all
                print_words(words)
                loop2 = True
            elif inp.check(0, 'f'): # Flip learn direction
                flip = not flip
            else: # Exit learning seession
                loop = False

def file_loop(file_name: str):
    ''' Start learning specific file. '''
    words = load_words(file_name)
    DEFAULT_WORDS_NUMBER = 10

    while True:
        console.cls()
        console.print(f"File: {Path(file_name).name} ({Word.get_avg_rate(words):.4})")
        console.print("[L N [fs] - learn; P [s] - print words; Q - quit; H - print help]")
        console.print("-----------------------------------------------------------------")
        inp = console.get_input()

        # Actions
        if inp.check(0, 'h'):
            console.print("[L] - Learn specific amount of words.")
            console.print(f"   (pos.arg:)[N] - Number of words for learing. (default: {DEFAULT_WORDS_NUMBER})")
            console.print("   (flag:)   [f] - Flip direction of languages.")
            console.print("   (flag:)   [s] - Pick lowest weight first.")
            console.print("   Example: 'l 10 s' - will start learning session with 10 words of lowest weight.\n")

            console.print("[P] - Print all words in current file.")
            console.print("   (flag:)   [s] - Sort by lowest weight first.\n")

            console.print("[Q] - Exit current file. Will return to file browser if started in interactive mode.")
            console.print("[QQ] - Terminate program.")
            console.print("[H] - Print this help.")
            console.print("[BCK] - Make backup of current file.")
            console.get_input()

        elif inp.check(0,'l'):
            count = inp.get_int(1, DEFAULT_WORDS_NUMBER)      # number of words
            flip = inp.check_flag(2, 'f')   # flip direction
            s = inp.check_flag(2, 's')      # pick lowest weight first

            words_in = []
            if s:
                words_in = get_sorted_by_rate(words)
            else:
                words_in = words
                random.shuffle(words_in)

            learn_loop(words_in, count, flip)
            store_words(file_name, words)

        elif inp.check(0,'qq'):
            exit()
        elif inp.check(0,'q'):
            return
        elif inp.check(0, 'p'):
            s = inp.check_flag(1, 's')
            print_words(words, s)
        elif inp.check(0, 'bck'):
            bck_dest = file_name + ".bck"
            shutil.copyfile(file_name, bck_dest)
        else:
            console.print("Unknown command.")
            console.get_input()

def pick_file_loop() -> str:
    ''' Show simple file explorer so user can pick a file to learn. '''
    curr_dir: Path = (Path(__file__).parent / "pkg")
    root_dir: Path = curr_dir
    curr_selection: int = 0
    curr_items: List[Path] = []
    rates: Dict[str, float] = {}
    rates_always: bool = False

    def cache_rate(e: Path, rates: Dict[str, float], force: bool = False):
        if force or (str(e) not in rates and e.is_file()):
            rates[str(e)] = Word.get_avg_rate(load_words(str(e)))

    while True:
        console.cls()
        console.print("Select file:") 
        console.print(f"[W/S - up/down; A/D - back/forth; C/V - show ratio.; Q - quit]{"(Always show rates)" if rates_always else ""}")
        console.print("--------------------------------------------------------------")

        # Print files
        for root, dirs, filenames in os.walk(curr_dir):
            for idx, entry in enumerate(dirs + filenames):
                s = (">" if idx == curr_selection else "")
                e = Path(root) / Path(entry)
                d = ("[DIR]" if e.is_dir() else "")
                if rates_always:
                    cache_rate(e, rates)
                r = (f"({str(rates[str(e)]):.6})" if str(e) in rates else "")

                console.print(f"{s:1} {d:5} {entry} {r}")

            curr_items = [Path(root) / Path(e) for e in chain(dirs, filenames)]
            break
        
        # Actions
        inp = console.get_input_ch()

        curr_entry = curr_items[curr_selection]
        if inp.check(0, 'v'):
            rates_always = not rates_always
        elif inp.check(0, 'q'):
            return ""
        elif inp.check(0, 's'):
            curr_selection = (curr_selection + 1) % len(curr_items)
        elif inp.check(0, 'w'):
            curr_selection = (curr_selection - 1) % len(curr_items)
        elif inp.check(0, 'a'): # Back
            if curr_dir != root_dir:
                curr_selection = 0
                curr_dir = curr_dir.parent
        elif inp.check(0, 'd'): # Forth
            if curr_entry.is_dir():
                curr_dir = curr_entry
            elif curr_entry.is_file() and curr_entry.suffix == ".txt":
                return str(curr_entry)
        elif inp.check(0, 'c'):
            cache_rate(curr_entry, rates, True)

def run(in_console: Any):
    if in_console:
        global console
        console = in_console

    # File from param or pick manually
    used_file_picker: bool = False
    file_name: str = ""
    if len(sys.argv) < 2:
        file_name = pick_file_loop()
        used_file_picker = True
    else:
        file_name = sys.argv[1]

    # Fallback to file picker if used after each loop.
    while True and file_name:
        file_loop(file_name)

        if not used_file_picker:
            break
        else:
            file_name = pick_file_loop()
    
    console.exit()

if __name__ == "__main__":
    run(SysConsole())
