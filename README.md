# SamLang – Mini Source-to-C Translator

## Overview

SamLang is a simple custom language translator built using Python. It converts `.sam` code into C, compiles it using GCC, and executes the program.

## Features

* Variable declaration (`let x = 10`)
* Arithmetic expressions
* Input handling (`input x`)
* Print statements
* Conditional logic (`if-else`)
* Basic error handling

## Example

### Input

```
input x

if x > 50
    print "High\n"
else
    print "Low\n"
```

### Output

```
Enter x: 78
High
```

## How to Run

```
python3 samlang.py test.sam
```

## Tech Stack

* Python
* C
* GCC

## Note

This is a simplified compiler-like project using string-based parsing.

