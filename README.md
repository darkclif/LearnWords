<p align="center">
    <img src="./media/logo.png" width="40%" >
</p>

justLearnWords
---

A tiny tool for people who want to learn words, not manage them.

- Tired of cluttered interface?
- Tired of endless configuration?
- You feel that you’re managing a database instead of learning words?

justLearnWords is just for you!

- Zero friction
- Minimal interface
- No cloud/blockchain/AI bullshit

Clone and run
---

### Clone
```
git clone https://github.com/darkclif/LearnWords
```

### Run
```
py learn.py 
- Interactive mode when you choose file from 'pkg' folder

py learn.py path/to/file.txt 
- Learn specific file
```

### Add
To add file with new words you should create TXT file with format:

```
word1_en;word1_it;0.0
word2_en;word2_it;0.0
...
```

- word1_en - Word in first language
- word1_it - Word in second language
- 0.0 - Starting weight, this will change during learning sessions.

Features
---

- Each word pair has weight assigned to it, it stays in range 0.0 to 1.0.
    - Values closer to 1.0 means you know the word.
    - Values closer to 0.0 means you do not.
- When you guess the word:
    - Correctly - adds 0.06 to weight.
    - Incorrectly - substracts 0.03 from weight.
    - Those values are hardcoded inside ```learn.py``` file.
- You can check average weight for given file from within interactive mode and also after selecting specific file.
- You can store additional context annotations inside parentheses. During learning sessions it will be presented on screen but ignored during correct answer detection.
    - Example: ``` to save (money);risparmiare;0.0 ``` - correct answer will be ```to save```.
- Multiple correct answers between slashes
    - Example: ``` work/function;funzionare;0.0  ``` - correct answers are ``` work ```  and ``` function ```.

Controls
---

Script has couple simple navigations screens:

- File picker
    - W/S/A/D - Navigate thorugh filesystem.
    - D - Select specific file.
    - C - Calculate average weight for all words inside file.
    - V - The same as C but does that for every file after you enter folder. It's not enabled by default in case you have HUGE amount of files inside single folder - in that case it can slow down the UI as weights are not cached anywhere.
    - Q - Exit program.
- File learning
    - L - Start learning session.
        - N - Positional argument. Number of words to learn. Example: ``` L 20 ``` will start with 20 random words. Default value is 10.
        - S - Flag. Pick words with lowest weight first. Example: ``` L 5 S ``` will start with 5 random words, lowest weight first. By default it will just pick fully random.
        - F - Flag. Start with flipped direction. If you have ``` word_it;word_en;0.0 ``` lines inside the file it will show english word first and you have to guess italian translation.
    - P - Print list of all words inside this file.
        - S - Flag. Sort ascending by weight.
    - BCK - Creates a backup of current file. In case of app crash it is worth to do it from time to time to save your weights.
    - H - Print help.
    - Q - Exit current file.
    - QQ - Fast exit. Exists the app without going back to file picker (if ran app without specific file as first argument). 
- Learning session
    - Typing ```Q``` isntead of taget word will quit current session without updating weights.
- Learning seesion end screen
 - R - Repeat same set.
 - F - Repear same set but with flipped direction.
 - P - Print all words from current set with new weights.
 - A - Add new words to current set and restart.
    - N - Positional argument. Number of words to add. Default is 0.

Sets
---

Ready to use sets available inside ```db``` subfolder! Feel free to contribute.