"""Brain Boost 2000 - an Android brain-test game (Kivy 2.4.0).

2,000 levels - maths, logic, memory, patterns, riddles and reasoning.
10 points per level, automatic saving, sound effects and animations.
"""
import json
import math
import os
import random
import struct
import time
import wave

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import (BooleanProperty, ListProperty, NumericProperty,
                             StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.widget import Widget




# ===================== PUZZLE ENGINE (2000 levels) =====================
import random
import re
from math import gcd

TOTAL = 2000
CATS = ["Maths", "Sequence", "Algebra", "Memory",
        "Pattern", "Logic", "Riddle", "Reasoning"]


def norm(s):
    """Normalise an answer for comparison."""
    s = str(s).lower().strip()
    s = re.sub(r"^(a|an|the)\s+", "", s)
    return re.sub(r"[^a-z0-9\-]", "", s)


def difficulty_name(lv):
    t = (lv - 1) / (TOTAL - 1)
    for limit, name in ((0.12, "Easy"), (0.35, "Medium"), (0.65, "Hard"),
                        (0.88, "Expert")):
        if t < limit:
            return name
    return "Genius"


def lerp(t, a, b):
    return int(a + (b - a) * t)


def P(cat, q, ans, hint, mem=None, secs=0.0):
    if not isinstance(ans, (list, tuple)):
        ans = [ans]
    return {"cat": cat, "q": q, "a": [norm(x) for x in ans],
            "hint": hint, "mem": mem, "secs": secs}


WORDS = ("apple river cloud tiger piano candle rocket garden planet window "
         "bridge pencil mirror forest island castle dragon silver thunder "
         "pirate puzzle jungle lantern compass harbor meadow falcon marble "
         "violin desert glacier anchor basket button cactus donkey eagle "
         "feather galaxy hammer igloo jacket kettle ladder magnet needle "
         "orange parrot quartz ribbon saddle turtle umbrella velvet walnut "
         "yogurt zipper").split()

NAMES = ("Alex Bella Chris Diana Ethan Fiona George Hannah Ivan Julia Kevin "
         "Laura Mason Nora Oscar Priya Quinn Ravi Sofia Tariq Uma Victor "
         "Wendy Xavier Yara Zane Amir Bruno Chloe Dev Elena Felix Grace "
         "Hugo Isla Jonas Kira Leo Maya Nico").split()

NONSENSE = ("Zorbs Blips Wugs Fleems Gribs Snarfs Tonks Plims Quibs Dorfs "
            "Yarps Mulls Vexes Brims Glorps Hinks Jaxes Kloms Narls Trebs "
            "Wimps Zinks Crads Frobs Spims").split()

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday"]

CLASSIC = [
    ("What has keys but cannot open locks?", ["piano", "keyboard"],
     "You can play music on it, or type with it."),
    ("What gets wetter the more it dries?", ["towel"],
     "You use it right after a shower."),
    ("I speak without a mouth and hear without ears. What am I?", ["echo"],
     "Shout in a canyon and listen."),
    ("What has hands but cannot clap?", ["clock", "watch"],
     "It tells you something every minute."),
    ("The more of me you take, the more you leave behind. What am I?",
     ["footsteps", "steps", "footstep", "step"],
     "Think about walking along a sandy beach."),
    ("What can you catch but never throw?", ["cold", "a cold"],
     "Sneezing is a symptom."),
    ("What has a head and a tail but no body?", ["coin"],
     "Flip it to decide something."),
    ("What goes up but never comes down?", ["age", "your age"],
     "Every birthday raises it."),
    ("What has many teeth but cannot bite?", ["comb"],
     "You use it on your hair."),
    ("What begins with T, ends with T, and has T inside it?", ["teapot"],
     "Tea is poured from it."),
    ("What can travel around the world while staying in a corner?",
     ["stamp"], "It sits on the corner of an envelope."),
    ("What has one eye but cannot see?", ["needle"],
     "Tailors thread it."),
    ("What is full of holes but still holds water?", ["sponge"],
     "You use it for washing up."),
    ("What belongs to you but other people use it more than you do?",
     ["name", "your name"], "People say it to get your attention."),
    ("What runs but never walks and has a mouth but never talks?",
     ["river"], "It flows to the sea."),
    ("What has a neck but no head?", ["bottle"],
     "You pour drinks from it."),
    ("What can fill a room but takes up no space?", ["light", "air"],
     "Switch it on."),
    ("What comes once in a minute, twice in a moment, but never in a "
     "thousand years?", ["m", "letter m", "the letter m"],
     "Look at the spelling of the words, not their meaning."),
    ("What word becomes shorter when you add two letters to it?",
     ["short"], "Add 'er' and see."),
    ("Forward I am heavy, backward I am not. What am I?", ["ton"],
     "Read it backwards: you get a word meaning 'not'."),
    ("What has four fingers and a thumb but is not alive?", ["glove"],
     "You wear it in winter."),
    ("What building has the most stories?", ["library"],
     "Think of books, not floors."),
    ("I have cities but no houses, mountains but no trees and water but "
     "no fish. What am I?", ["map"], "You unfold it to find your way."),
    ("What has legs but cannot walk?", ["table", "chair", "bed", "desk"],
     "You find it in a home."),
    ("What can you break without ever touching it?", ["promise", "silence"],
     "Keeping it is the opposite."),
    ("What is always in front of you but cannot be seen?", ["future"],
     "It hasn't happened yet."),
    ("What gets bigger the more you take away from it?", ["hole"],
     "Dig and see."),
    ("Which month has 28 days?", ["all", "every month", "all of them",
                                   "all months"],
     "Does February have the only 28th day?"),
    ("What flies without wings and cries without eyes?", ["cloud", "clouds"],
     "Look up when it rains."),
    ("What has a thumb and four fingers but never needs a manicure?",
     ["glove", "mitten"], "Hands wear it."),
]


# ---------------------------------------------------------------- Maths
def g_maths(lv, r, t, v):
    k = v % 4
    if k == 0:
        n = 2 + int(t * 3.99)
        hi = lerp(t, 9, 400)
        nums = [r.randint(2, hi) for _ in range(n)]
        ops = [r.choice("+-*") for _ in range(n - 1)]
        for i, o in enumerate(ops):
            if o == "*":
                m = lerp(t, 5, 30)
                nums[i], nums[i + 1] = r.randint(2, m), r.randint(2, m)
        expr = str(nums[0])
        for o, x in zip(ops, nums[1:]):
            expr += " %s %d" % (o, x)
        ans = eval(expr)
        shown = expr.replace("*", "\u00d7")
        if "*" in ops:
            i = ops.index("*")
            hint = ("Multiplication comes first: %d \u00d7 %d = %d. Then add "
                    "and subtract from left to right." %
                    (nums[i], nums[i + 1], nums[i] * nums[i + 1]))
        else:
            first = eval("%d %s %d" % (nums[0], ops[0], nums[1]))
            hint = ("Work from left to right. Start with %d %s %d = %d." %
                    (nums[0], ops[0], nums[1], first))
        return P("Maths", "Calculate:\n" + shown, ans, hint)
    if k == 1:
        p = r.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 120,
                      150][:6 + int(t * 7)])
        m = 100 // gcd(p, 100)
        n = m * r.randint(1, lerp(t, 10, 200))
        return P("Maths", "What is %d%% of %d?" % (p, n), n * p // 100,
                 "%d%% means %d/100. Work out %d \u00d7 %d = %d, then "
                 "divide by 100." % (p, p, n, p, n * p))
    if k == 2:
        a = r.randint(11, lerp(t, 30, 999))
        b = r.randint(3, lerp(t, 12, 99))
        tens, u = a // 10 * 10, a % 10
        return P("Maths", "What is %d \u00d7 %d?" % (a, b), a * b,
                 "Split %d into %d + %d. Then %d \u00d7 %d = %d and "
                 "%d \u00d7 %d = %d. Add them." %
                 (a, tens, u, tens, b, tens * b, u, b, u * b))
    s = (v // 4) % 3
    if s == 0:
        n = r.randint(lerp(t, 20, 200), lerp(t, 60, 5000))
        d = r.randint(3, lerp(t, 9, 60))
        return P("Maths", "What is the remainder when %d is divided by %d?"
                 % (n, d), n % d,
                 "%d \u00d7 %d = %d is the closest multiple below %d. How "
                 "much is left over?" % (d, n // d, d * (n // d), n))
    if s == 1:
        n = r.randint(lerp(t, 8, 30), lerp(t, 15, 300))
        return P("Maths", "Add all whole numbers from 1 to %d." % n,
                 n * (n + 1) // 2,
                 "Pair first and last: 1 + %d = %d. There are %d/2 such "
                 "pairs, i.e. n(n+1)/2." % (n, n + 1, n))
    a = r.randint(12, lerp(t, 25, 199))
    return P("Maths", "What is %d squared?" % a, a * a,
             "Split %d = %d + %d, then use (x+y)\u00b2 = x\u00b2 + 2xy + "
             "y\u00b2." % (a, a // 10 * 10, a % 10))


# ------------------------------------------------------------- Sequence
def g_sequence(lv, r, t, v):
    k = v % 6
    if k == 0:
        d = r.randint(2, lerp(t, 6, 80)) * r.choice([1, -1] if t > .2 else [1])
        s0 = r.randint(-lerp(t, 0, 60), lerp(t, 20, 400))
        seq = [s0 + d * i for i in range(5)]
        ans = s0 + d * 5
        hint = ("Look at the gap between neighbours: %d to %d is a change of "
                "%d. The same step repeats." % (seq[0], seq[1], d))
    elif k == 1:
        ratio = r.randint(2, 3 + int(t * 3))
        s0 = r.randint(1, lerp(t, 5, 12))
        seq = [s0 * ratio ** i for i in range(5)]
        ans = s0 * ratio ** 5
        hint = "Divide each term by the one before: %d \u00f7 %d = %d." % (
            seq[1], seq[0], ratio)
    elif k == 2:
        d1 = r.randint(1, lerp(t, 4, 30))
        c = r.randint(1, lerp(t, 3, 15))
        s0 = r.randint(0, lerp(t, 10, 200))
        seq = [s0]
        for i in range(6):
            seq.append(seq[-1] + d1 + c * i)
        ans = seq.pop() 
        gaps = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
        hint = ("The gaps are %s. Notice how the gaps themselves grow by the "
                "same amount each time." % ", ".join(map(str, gaps)))
    elif k == 3:
        a, b = r.randint(1, lerp(t, 5, 40)), r.randint(1, lerp(t, 8, 60))
        if t > 0.55:
            c = r.randint(1, lerp(t, 5, 30))
            seq = [a, b, c]
            for _ in range(4):
                seq.append(seq[-1] + seq[-2] + seq[-3])
            ans = seq[-1] + seq[-2] + seq[-3]
            hint = ("Each term is the sum of the previous THREE: %d + %d + "
                    "%d = %d." % (a, b, c, a + b + c))
        else:
            seq = [a, b]
            for _ in range(4):
                seq.append(seq[-1] + seq[-2])
            ans = seq[-1] + seq[-2]
            hint = ("Each term is the sum of the previous two: %d + %d = %d."
                    % (a, b, a + b))
    elif k == 4:
        a0, p = r.randint(1, lerp(t, 10, 100)), r.randint(1, lerp(t, 5, 40))
        b0, q = r.randint(1, lerp(t, 10, 100)), r.randint(2, lerp(t, 8, 50))
        seq = []
        for i in range(4):
            seq += [a0 + p * i, b0 + q * i]
        seq = seq[:7]
        hint = ("Two patterns are mixed together. Take every other number: "
                "%s (step %d) and %s (step %d)." % (
                    ", ".join(str(x) for x in seq[0::2]), p,
                    ", ".join(str(x) for x in seq[1::2]), q))
        ans = b0 + q * 3  # 7 terms shown; the next one is the 4th 'b' term
    else:
        c = r.randint(1, lerp(t, 10, 60))
        o = r.randint(1, lerp(t, 8, 40))
        if t > 0.7 and r.random() < .5:
            seq = [(o + i) ** 3 + c for i in range(5)]
            ans = (o + 5) ** 3 + c
            hint = "These are cubes plus %d. Subtract %d from %d: you get %d = %d\u00b3." % (
                c, c, seq[0], seq[0] - c, o)
        else:
            seq = [(o + i) ** 2 + c for i in range(5)]
            ans = (o + 5) ** 2 + c
            hint = "These are perfect squares plus %d. %d - %d = %d = %d\u00b2." % (
                c, seq[0], c, seq[0] - c, o)
    return P("Sequence", "What number comes next?\n" + ",  ".join(map(str, seq))
             + ",  ?", ans, hint)


# -------------------------------------------------------------- Algebra
def g_algebra(lv, r, t, v):
    k = v % 5
    if k == 0:
        a = r.randint(2, lerp(t, 6, 30))
        x = r.randint(2, lerp(t, 12, 150)) * (-1 if t > .6 and r.random() < .3 else 1)
        b = r.randint(1, lerp(t, 20, 300))
        if r.random() < .5:
            c = a * x + b
            q = "Solve for x:\n%dx + %d = %d" % (a, b, c)
            hint = "Move %d across: %dx = %d. Then divide by %d." % (b, a, c - b, a)
        else:
            c = a * x - b
            q = "Solve for x:\n%dx - %d = %d" % (a, b, c)
            hint = "Add %d to both sides: %dx = %d. Then divide by %d." % (b, a, c + b, a)
        return P("Algebra", q, x, hint)
    if k == 1:
        a = r.randint(2, lerp(t, 9, 40))
        x = r.randint(2, lerp(t, 15, 200))
        b = r.randint(1, lerp(t, 15, 150))
        c = (x + b) * a
        return P("Algebra", "Find x:\n(x + %d) \u00d7 %d = %d" % (b, a, c), x,
                 "Divide both sides by %d first: x + %d = %d." % (a, b, c // a))
    if k == 2:
        x = r.randint(3, lerp(t, 15, 120))
        y = r.randint(1, x - 1)
        s_, d_ = x + y, x - y
        if t > 0.5:
            return P("Algebra", "x + y = %d\nx - y = %d\nWhat is x \u00d7 y?" % (s_, d_),
                     x * y, "Add the equations: 2x = %d, so x = %d. Then find "
                     "y from x + y = %d." % (s_ + d_, (s_ + d_) // 2, s_))
        return P("Algebra", "x + y = %d\nx - y = %d\nWhat is x?" % (s_, d_), x,
                 "Add the two equations: 2x = %d + %d = %d." % (s_, d_, s_ + d_))
    if k == 3:
        a = r.randint(2, lerp(t, 9, 40))
        b = r.randint(1, lerp(t, 15, 150))
        q_ = r.randint(1, lerp(t, 12, 120))
        c = q_ + b
        return P("Algebra", "Solve for x:\nx \u00f7 %d + %d = %d" % (a, b, c), a * q_,
                 "Subtract %d: x \u00f7 %d = %d. Now multiply by %d." % (b, a, q_, a))
    r1 = r.randint(1, lerp(t, 6, 30))
    r2 = r.randint(1, lerp(t, 6, 30))
    return P("Algebra", "Find the larger root of:\nx\u00b2 - %dx + %d = 0" % (
        r1 + r2, r1 * r2), max(r1, r2),
        "Find two numbers that add up to %d and multiply to %d." % (
            r1 + r2, r1 * r2))


# --------------------------------------------------------------- Memory
def g_memory(lv, r, t, v):
    k = v % 5
    if k in (0, 1):
        n = 3 + int(t * 7.99) - (1 if k == 1 else 0)
        digs = "".join(str(r.randint(0, 9)) for _ in range(n))
        secs = 1.2 + 0.6 * n
        if k == 0:
            q = "Type the %d digits you just saw." % n
            hint = ("Chunk them in groups of two or three. It starts with %s "
                    "and ends with %s." % (digs[0], digs[-1]))
            ans = digs
        else:
            q = "Type the %d digits you just saw in REVERSE order." % n
            hint = ("Read the sequence from the end. Your answer starts with "
                    "%s." % digs[-1])
            ans = digs[::-1]
        return P("Memory", q, ans, hint, mem="  ".join(digs), secs=secs)
    if k == 2:
        n = 3 + int(t * 5.99)
        ws = r.sample(WORDS, n)
        p = r.randint(2, n)
        q = "Which word was in position %d of %d?" % (p, n)
        hint = ("Link the words in a little story. Position %d comes right "
                "after '%s'." % (p, ws[p - 2]))
        return P("Memory", q, ws[p - 1], hint, mem="\n".join(ws),
                 secs=1.5 + 0.9 * n)
    if k == 3:
        rows, cols = 3 + int(t * 2.99), 4 + int(t * 2.99)
        syms = r.sample("AKMRTX", 2 + (1 if t > .4 else 0))
        grid = [[r.choice(syms) for _ in range(cols)] for _ in range(rows)]
        target = syms[0]
        cnt = sum(row.count(target) for row in grid)
        if cnt == 0:
            grid[0][0] = target
            cnt = sum(row.count(target) for row in grid)
        text = "\n".join("   ".join(row) for row in grid)
        hint = ("Count row by row. The first row has %d '%s'." %
                (grid[0].count(target), target))
        return P("Memory", "How many times did the letter '%s' appear?" % target,
                 cnt, hint, mem=text, secs=2.5 + rows * cols * 0.35)
    n = 4 + int(t * 5.99)
    digs = [r.randint(1, 9) for _ in range(n)]
    return P("Memory", "What is the SUM of the %d digits you just saw?" % n,
             sum(digs),
             "Add them in pairs. The first two digits add up to %d." %
             (digs[0] + digs[1]),
             mem="  ".join(map(str, digs)), secs=1.5 + 0.7 * n)


# -------------------------------------------------------------- Pattern
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def g_pattern(lv, r, t, v):
    k = v % 4
    if k == 0:
        s = r.randint(1, lerp(t, 3, 12))
        i0 = r.randint(0, 25)
        items = [ALPHA[(i0 + s * i) % 26] for i in range(5)]
        ans = ALPHA[(i0 + s * 5) % 26]
        return P("Pattern", "Which letter comes next?\n" + ",  ".join(items) + ",  ?",
                 ans, "Each letter jumps %d place(s) forward in the alphabet "
                 "(%s to %s). After Z it wraps around to A." % (s, items[0], items[1]))
    if k == 1:
        s = r.randint(1, lerp(t, 3, 8))
        i0 = r.randint(0, 25 - s * 4) if 25 - s * 4 > 0 else 0
        n0, m = r.randint(1, lerp(t, 9, 60)), r.randint(1, lerp(t, 4, 15))
        items = ["%s%d" % (ALPHA[(i0 + s * i) % 26], n0 + m * i) for i in range(4)]
        ans = "%s%d" % (ALPHA[(i0 + s * 4) % 26], n0 + m * 4)
        return P("Pattern", "What comes next?\n" + ",  ".join(items) + ",  ?",
                 ans, "Two patterns at once: letters jump %d place(s) and the "
                 "numbers go up by %d." % (s, m))
    if k == 2:
        u = 2 + int(t * 3.99)
        unit = r.sample("RGBYPO", u)
        shown = u * 2 + r.randint(0, u - 1)
        n = r.randint(shown + 2, lerp(t, 15, 250))
        seq = [unit[i % u] for i in range(shown)]
        ans = unit[(n - 1) % u]
        pos = (n - 1) % u + 1
        return P("Pattern", "Colour code repeats forever:\n%s ...\nWhich letter is item number %d?" % (
            " ".join(seq), n), ans,
            "The pattern repeats every %d items. %d divided by %d leaves "
            "remainder %d, so look at position %d of the pattern." % (
                u, n, u, n % u, pos))
    maxlen = 4 + int(t * 6)
    pool = [w for w in WORDS if len(w) <= maxlen] or WORDS
    w = r.choice(pool)
    s = r.randint(1, 25)
    enc = "".join(ALPHA[(ALPHA.index(c.upper()) + s) % 26] for c in w)
    return P("Pattern", "Secret code: every letter was moved FORWARD %d places "
             "in the alphabet.\nDecode:  %s" % (s, enc), w,
             "Move each letter BACK %d places. For example %s becomes %s." % (
                 s, enc[0], w[0].upper()))


# ---------------------------------------------------------------- Logic
ORDERS = [("taller", "tallest", "shortest"), ("older", "oldest", "youngest"),
          ("faster", "fastest", "slowest"), ("heavier", "heaviest", "lightest")]
ORD_NAMES = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh"]


def g_logic(lv, r, t, v):
    k = v % 4
    if k == 0:
        n = 3 + int(t * 3.99)
        order = r.sample(NAMES, n)            # order[0] is the "most"
        comp, most, least = r.choice(ORDERS)
        st = []
        for i in range(n - 1):
            a, b = order[i], order[i + 1]
            if t > .3 and r.random() < .5:
                st.append("%s is %s than %s." % (b, comp.replace("taller", "shorter")
                          .replace("older", "younger").replace("faster", "slower")
                          .replace("heavier", "lighter"), a))
            else:
                st.append("%s is %s than %s." % (a, comp, b))
        r.shuffle(st)
        if t > .45 and n >= 4:
            p = r.randint(2, n - 1)
            q = "Who is %s in order from the %s?" % (ORD_NAMES[p], most)
            hint = ("Link the statements into one chain from %s to %s. The "
                    "chain starts with %s." % (most, least, order[0]))
            ans = order[p - 1]
        elif r.random() < .5:
            q, ans = "Who is the %s?" % most, order[0]
            hint = ("The %s person never appears as the weaker one in any "
                    "statement." % most)
        else:
            q, ans = "Who is the %s?" % least, order[-1]
            hint = ("The %s person never appears as the stronger one in any "
                    "statement." % least)
        return P("Logic", " ".join(st) + "\n" + q, ans, hint)
    if k == 1:
        n = 4 + int(t * 2.99)
        m = r.randint(3, lerp(t, 9, 40))
        mult = [m * r.randint(1, lerp(t, 8, 60)) for _ in range(n - 1)]
        odd = m * r.randint(1, lerp(t, 8, 60)) + r.randint(1, m - 1)
        nums = mult + [odd]
        if len(set(nums)) < n:
            nums = list(dict.fromkeys(nums))
            while len(nums) < n:
                nums.insert(0, m * r.randint(60, 90))
        r.shuffle(nums)
        return P("Logic", "Which number does NOT belong with the others?\n" +
                 ",  ".join(map(str, nums)), odd,
                 "All but one share a divisibility rule with %d. Test %d "
                 "\u00f7 %d = %.2f." % (m, mult[0], m, mult[0] / m))
    if k == 2:
        n = 3 + int(t * 4.99)
        names = ALPHA[:n + 1]
        val = r.randint(2, lerp(t, 9, 40))
        lines = ["A = %d" % val]
        vals = [val]
        first_step = ""
        for i in range(1, n + 1):
            op = r.choice(["+", "-", "*"]) if i > 1 or t > .2 else r.choice("+*")
            c = r.randint(2, lerp(t, 5, 12))
            prev = names[i - 1]
            nv = eval("%d %s %d" % (vals[-1], op, c))
            lines.append("%s = %s %s %d" % (names[i], prev, op.replace("*", "\u00d7"), c))
            if i == 1:
                first_step = "A = %d, so B = %d %s %d = %d." % (
                    val, val, op.replace("*", "\u00d7"), c, nv)
            vals.append(nv)
        return P("Logic", "\n".join(lines) + "\nWhat is %s?" % names[n], vals[-1],
                 "Compute step by step. " + first_step)
    L = 2 + int(t * 3.99)
    ws = r.sample(NONSENSE, L + 1)
    prem = ["All %s are %s." % (ws[i], ws[i + 1]) for i in range(L)]
    if r.random() < .5:
        q = "Is every %s also a %s? (yes/no)" % (ws[0].rstrip("s").lower(),
                                                ws[-1].rstrip("s").lower())
        ans, hint = "yes", ("Chain the statements: %s -> %s -> ... -> %s. "
                            "Each link passes the property along." % (ws[0], ws[1], ws[-1]))
    else:
        q = "Is every %s also a %s? (yes/no)" % (ws[-1].rstrip("s").lower(),
                                                ws[0].rstrip("s").lower())
        ans, hint = "no", ("The statements only work in one direction: from %s "
                           "towards %s, not backwards." % (ws[0], ws[-1]))
    return P("Logic", "\n".join(prem) + "\n" + q, [ans, ans[0]], hint)


# --------------------------------------------------------------- Riddle
def number_riddle(lv, r, t):
    digits = 2 + int(t * 2.99)
    lo, hi = 10 ** (digits - 1), 10 ** digits - 1
    for _ in range(200):
        target = r.randint(lo, hi)
        ds = [int(c) for c in str(target)]
        pool = []
        s = sum(ds)
        pool.append(("my digits add up to %d" % s, lambda n, s=s: sum(map(int, str(n))) == s))
        pool.append(("I am %s" % ("even" if target % 2 == 0 else "odd"),
                     lambda n, e=target % 2: n % 2 == e))
        divs = [d for d in range(3, 20) if target % d == 0]
        if divs:
            d = r.choice(divs)
            pool.append(("I am a multiple of %d" % d, lambda n, d=d: n % d == 0))
        else:
            d = r.randint(3, 9)
            pool.append(("when divided by %d I leave remainder %d" % (d, target % d),
                         lambda n, d=d, m=target % d: n % d == m))
        if 0 not in ds:
            p = 1
            for x in ds:
                p *= x
            pool.append(("the product of my digits is %d" % p,
                         lambda n, p=p: eval("*".join(str(n))) == p))
        pool.append(("my last digit is %d" % ds[-1], lambda n, e=ds[-1]: n % 10 == e))
        pool.append(("my first digit is %d" % ds[0], lambda n, e=ds[0]: int(str(n)[0]) == e))
        m = target - r.randint(1, max(2, (hi - lo) // 6))
        pool.append(("I am greater than %d" % m, lambda n, m=m: n > m))
        m2 = target + r.randint(1, max(2, (hi - lo) // 6))
        pool.append(("I am less than %d" % m2, lambda n, m=m2: n < m))
        r.shuffle(pool)
        cands = list(range(lo, hi + 1))
        used, sizes = [], []
        for text, f in pool:
            cands = [n for n in cands if f(n)]
            used.append(text)
            sizes.append(len(cands))
            if len(cands) == 1:
                break
        if len(cands) == 1 and len(used) <= 6:
            q = ("I am a %d-digit number.\n" % digits +
                 "\n".join("- " + u[0].upper() + u[1:] + "." for u in used) +
                 "\nWhat number am I?")
            hint = ("Start with the clue \"%s\". It leaves about %d "
                    "candidates. Then test them against the next clue." % (
                        used[0], sizes[0]))
            return P("Riddle", q, target, hint)
    raise RuntimeError("number riddle failed")


def age_riddle(lv, r, t):
    a, b = r.sample(NAMES, 2)
    g = r.randint(2, 2 + int(t * 4))
    f = g + r.randint(1, 1 + int(t * 3))
    m = r.randint(1, lerp(t, 6, 20))
    age_b, y = (g - 1) * m, m * (f - g)
    q = ("%s is %d times as old as %s. In %d years, %s will be %d times as old "
         "as %s.\nHow old is %s now?" % (a, f, b, y, a, g, b, b))
    hint = ("Let %s's age be x, so %s = %dx. In %d years: %dx + %d = %d(x + %d). "
            "Solve for x." % (b, a, f, y, f, y, g, y))
    return P("Riddle", q, age_b, hint)


def g_riddle(lv, r, t, v):
    if v < len(CLASSIC):
        q, a, h = CLASSIC[v]
        return P("Riddle", q, a, h)
    return number_riddle(lv, r, t) if (v % 2 == 0) else age_riddle(lv, r, t)


# ------------------------------------------------------------ Reasoning
def g_reasoning(lv, r, t, v):
    k = v % 7
    if k == 0:
        n = r.randint(lerp(t, 4, 20), lerp(t, 8, 300))
        return P("Reasoning", "At a party %d people each shake hands exactly "
                 "once with every other person. How many handshakes happen?" % n,
                 n * (n - 1) // 2,
                 "Each of the %d people shakes %d hands, but every handshake is "
                 "counted twice. Compute %d \u00d7 %d, then halve it." % (
                     n, n - 1, n, n - 1))
    if k == 1:
        d0 = r.randrange(7)
        n = r.randint(lerp(t, 8, 40), lerp(t, 30, 5000))
        back = t > .5 and r.random() < .4
        res = DAYS[(d0 - n) % 7] if back else DAYS[(d0 + n) % 7]
        word = "ago" if back else "from now"
        return P("Reasoning", "Today is %s. What day of the week is it %d days %s?" % (
            DAYS[d0], n, word), [res, res[:3]],
            "A week has 7 days. %d \u00f7 7 leaves remainder %d, so move %d "
            "day(s) %s from %s." % (n, n % 7, n % 7, "back" if back else "forward", DAYS[d0]))
    if k == 2:
        h = r.randint(1, 12)
        m = r.choice(range(0, 60, 10 if t < .4 else 2))
        hh = (h % 12) * 30 + m * 0.5
        mm = m * 6
        ang = abs(hh - mm)
        if ang > 180:
            ang = 360 - ang
        return P("Reasoning", "What is the smaller angle (in degrees) between the "
                 "clock hands at %d:%02d?" % (h, m), int(ang),
                 "The minute hand is at %d\u00b0. The hour hand is at %g\u00b0 (30\u00b0 "
                 "per hour plus 0.5\u00b0 per minute). Subtract." % (mm, hh))
    if k == 3:
        x = r.randint(2, lerp(t, 6, 24))
        d = r.randint(2, lerp(t, 8, 40))
        tot = x * d
        divs = [y for y in range(1, tot + 1) if tot % y == 0 and y != x]
        y = r.choice(divs)
        return P("Reasoning", "%d painters need %d days to paint a school. How many "
                 "days would %d painters need (same speed)?" % (x, d, y), tot // y,
                 "Total work = %d \u00d7 %d = %d painter-days. Divide by %d." % (x, d, tot, y))
    if k == 4:
        v_ = 4 * r.randint(5, lerp(t, 25, 40))
        hrs = r.randint(1, lerp(t, 3, 9))
        mins = r.choice([15, 30, 45])
        dist = v_ * hrs + v_ * mins // 60
        return P("Reasoning", "A car travels at %d km/h. How many km does it cover "
                 "in %d hour(s) and %d minutes?" % (v_, hrs, mins), dist,
                 "Full hours give %d km. %d minutes is %d/4 of an hour, so take "
                 "that share of %d km." % (v_ * hrs, mins, mins // 15, v_))
    if k == 5:
        n = r.randint(lerp(t, 5, 20), lerp(t, 12, 200))
        g = r.randint(2, lerp(t, 6, 15))
        if r.random() < .5:
            return P("Reasoning", "A straight fence has %d posts, each exactly %d m "
                     "from the next. How long is the fence?" % (n, g), (n - 1) * g,
                     "%d posts make only %d gaps. Multiply the gaps by %d." % (n, n - 1, g))
        return P("Reasoning", "%d lamps are placed around a circular pond, each exactly "
                 "%d m from the next. How far is it around the pond?" % (n, g), n * g,
                 "On a circle the number of gaps equals the number of lamps: %d." % n)
    N = r.randint(lerp(t, 30, 120), lerp(t, 99, 999))
    D = r.randint(1, 9)
    cnt = sum(str(i).count(str(D)) for i in range(1, N + 1))
    parts = []
    for p, nm in ((1, "units"), (10, "tens"), (100, "hundreds")):
        if p <= N:
            parts.append("%s place: %d" % (nm, sum(1 for i in range(1, N + 1)
                                                    if (i // p) % 10 == D and i >= p)))
    return P("Reasoning", "How many times is the digit %d written when you write every "
             "whole number from 1 to %d?" % (D, N), cnt,
             "Count place by place. " + "; ".join(parts[:-1] or parts) +
             ". Add up all the places.")


GENS = [g_maths, g_sequence, g_algebra, g_memory, g_pattern, g_logic,
        g_riddle, g_reasoning]


def make_level(lv, seen):
    """Build puzzle number `lv` (1-based), guaranteeing a unique puzzle."""
    cat = (lv - 1) % 8
    v = (lv - 1) // 8
    t0 = (lv - 1) / (TOTAL - 1)
    for attempt in range(400):
        t = min(1.0, t0 + 0.003 * attempt)
        r = random.Random(lv * 7919 + attempt * 104729 + 13)
        p = GENS[cat](lv, r, t, v)
        key = (p["q"], p["mem"])
        if key not in seen:
            seen.add(key)
            p["lv"] = lv
            return p
    raise RuntimeError("could not make unique level %d" % lv)


def iter_levels():
    """Yield puzzles for levels 1..TOTAL one at a time."""
    seen = set()
    for lv in range(1, TOTAL + 1):
        yield make_level(lv, seen)


# ============================== GAME ==============================
Window.clearcolor = (0.04, 0.05, 0.12, 1)

POINTS_PER_LEVEL = 10
LOOKAHEAD = 10          # you may play up to 10 levels past your furthest win
PAGE = 50               # levels per page on the level-select screen

RANKS = [(0, "Rookie"), (10, "Apprentice"), (50, "Thinker"), (150, "Puzzler"),
         (400, "Strategist"), (800, "Mastermind"), (1200, "Genius"),
         (1700, "Legend"), (2000, "Brain Boost Champion")]


# ------------------------------------------------------------------ sound
def make_wav(path, notes, vol=0.5, rate=22050):
    frames = bytearray()
    for freq, dur in notes:
        n = int(rate * dur)
        for i in range(n):
            env = min(1.0, i / (rate * 0.01)) * min(1.0, (n - i) / (rate * 0.05))
            v = 0.0
            if freq:
                v = (math.sin(2 * math.pi * freq * i / rate) +
                     0.3 * math.sin(4 * math.pi * freq * i / rate)) / 1.3
            frames += struct.pack("<h", int(32767 * vol * env * v))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


SFX_DEFS = {
    "tap": [(660, 0.05)],
    "correct": [(523, 0.09), (659, 0.09), (784, 0.18)],
    "win": [(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.1), (784, 0.08),
            (1047, 0.3)],
    "wrong": [(220, 0.12), (165, 0.22)],
    "hint": [(880, 0.07), (1175, 0.12)],
    "go": [(440, 0.06), (587, 0.1)],
}


class Sfx:
    def __init__(self, folder, store):
        self.store = store
        self.sounds = {}
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception:
            return
        for name, notes in SFX_DEFS.items():
            path = os.path.join(folder, name + ".wav")
            try:
                if not os.path.exists(path):
                    make_wav(path, notes)
                self.sounds[name] = SoundLoader.load(path)
            except Exception:
                self.sounds[name] = None

    def play(self, name):
        if not self.store.data.get("sound", True):
            return
        s = self.sounds.get(name)
        if s:
            try:
                s.volume = float(self.store.data.get("volume", 0.7))
                s.stop()
                s.play()
            except Exception:
                pass


# ------------------------------------------------------------------- save
class Store:
    DEFAULT = {"solved": [], "hinted": [], "last": 1, "sound": True,
               "volume": 0.7, "anim": True}

    def __init__(self, path):
        self.path = path
        self.data = json.loads(json.dumps(self.DEFAULT))
        try:
            with open(path, "r") as f:
                d = json.load(f)
            for k in self.DEFAULT:
                if k in d:
                    self.data[k] = d[k]
        except Exception:
            pass
        self.solved = set(int(x) for x in self.data["solved"])
        self.hinted = set(int(x) for x in self.data["hinted"])

    def save(self):
        self.data["solved"] = sorted(self.solved)
        self.data["hinted"] = sorted(self.hinted)
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(self.data, f)
            os.replace(tmp, self.path)
        except Exception:
            pass

    def reset(self):
        self.solved, self.hinted = set(), set()
        self.data["last"] = 1
        self.save()

    def reach(self):
        return min(TOTAL, max(self.solved, default=0) + LOOKAHEAD)

    def next_unsolved(self):
        for n in range(1, TOTAL + 1):
            if n not in self.solved:
                return n
        return TOTAL


# ---------------------------------------------------------------- widgets
class RBtn(ButtonBehavior, Label):
    bg = ListProperty([0.49, 0.36, 1, 1])
    rad = NumericProperty(dp(18))

    def on_press(self):
        app = App.get_running_app()
        if app:
            app.sfx.play("tap")
        if not hasattr(self, "_fs0"):
            self._fs0 = self.font_size
        Animation.cancel_all(self, "font_size")
        Animation(font_size=self._fs0 * 0.92, d=0.06).start(self)

    def on_release(self):
        if hasattr(self, "_fs0"):
            Animation(font_size=self._fs0, d=0.1).start(self)


class Card(BoxLayout):
    bg = ListProperty([0.11, 0.13, 0.26, 1])


class Bar(Widget):
    value = NumericProperty(0)
    col = ListProperty([0.49, 0.36, 1, 1])


class Dot(Widget):
    col = ListProperty([1, 1, 1, 1])


def left_label(text, **kw):
    lb = Label(text=text, halign="left", valign="middle", **kw)
    lb.bind(size=lambda w, s: setattr(w, "text_size", s))
    return lb


KV = """
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<Screen>:
    canvas.before:
        Color:
            rgba: .04, .05, .12, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: .49, .36, 1, .13
        Ellipse:
            pos: self.x + self.width - dp(210), self.y + self.height - dp(210)
            size: dp(340), dp(340)
        Color:
            rgba: .1, .8, .9, .09
        Ellipse:
            pos: self.x - dp(130), self.y - dp(110)
            size: dp(320), dp(320)

<RBtn>:
    size_hint_y: None
    height: dp(52)
    font_size: sp(17)
    bold: True
    color: 1, 1, 1, 1
    opacity: .45 if self.disabled else 1
    canvas.before:
        Color:
            rgba: (self.bg[0] * .72, self.bg[1] * .72, self.bg[2] * .72, self.bg[3]) if self.state == 'down' else self.bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.rad, ]

<Card>:
    canvas.before:
        Color:
            rgba: self.bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(22), ]

<Bar>:
    canvas:
        Color:
            rgba: .17, .19, .36, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2, ]
        Color:
            rgba: self.col
        RoundedRectangle:
            pos: self.pos
            size: max(self.width * self.value, self.height if self.value > 0 else 0), self.height
            radius: [self.height / 2, ]

<Dot>:
    canvas:
        Color:
            rgba: self.col
        Ellipse:
            pos: self.pos
            size: self.size

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24), dp(22)
        spacing: dp(10)
        Label:
            id: logo
            text: 'BRAIN BOOST'
            font_size: sp(40)
            bold: True
            color: .8, .74, 1, 1
            size_hint_y: None
            height: dp(60)
        Label:
            id: logo2
            text: '2000'
            font_size: sp(84)
            bold: True
            color: .15, .88, .96, 1
            size_hint_y: None
            height: dp(90)
        Label:
            text: 'The ultimate brain-test challenge'
            font_size: sp(15)
            color: .7, .74, .92, 1
            size_hint_y: None
            height: dp(26)
        Card:
            size_hint_y: None
            height: dp(64)
            padding: dp(16), 0
            Label:
                text: app.rank
                bold: True
                font_size: sp(17)
                color: .8, .74, 1, 1
            Label:
                text: str(int(app.points)) + ' pts'
                bold: True
                font_size: sp(20)
                color: 1, .82, .3, 1
        Widget:
        Label:
            text: app.load_text if not app.ready else ''
            font_size: sp(13)
            color: .6, .65, .85, 1
            size_hint_y: None
            height: dp(20)
        RBtn:
            id: b1
            text: app.play_text
            disabled: not app.ready
            bg: .2, .78, .5, 1
            on_release: app.play()
        RBtn:
            id: b2
            text: 'LEVELS'
            disabled: not app.ready
            bg: .49, .36, 1, 1
            on_release: app.open_levels()
        RBtn:
            id: b3
            text: 'PROGRESS'
            bg: .1, .62, .85, 1
            on_release: app.goto('progress')
        RBtn:
            id: b4
            text: 'SETTINGS'
            bg: .3, .33, .55, 1
            on_release: app.goto('settings')

<GameScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(8)
        BoxLayout:
            size_hint_y: None
            height: dp(46)
            spacing: dp(8)
            RBtn:
                text: 'Back'
                size_hint_x: None
                width: dp(76)
                height: dp(44)
                font_size: sp(15)
                rad: dp(14)
                bg: .17, .19, .36, 1
                on_release: app.back_to_levels()
            Label:
                text: root.title_text
                font_size: sp(22)
                bold: True
            Label:
                text: str(int(app.points)) + ' pts'
                size_hint_x: None
                width: dp(92)
                color: 1, .82, .3, 1
                bold: True
        Label:
            text: root.cat_text
            font_size: sp(14)
            color: .15, .88, .96, 1
            size_hint_y: None
            height: dp(22)
        Card:
            id: qcard
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(8)
            Label:
                text: root.q_text
                font_size: root.q_size
                halign: 'center'
                valign: 'middle'
                text_size: self.size
            Bar:
                size_hint_y: None
                height: dp(8)
                value: root.mem_frac
                col: .15, .88, .96, 1
                opacity: 1 if root.phase == 'memory' else 0
        Label:
            id: hintlbl
            text: root.hint_text
            font_size: sp(15)
            color: 1, .82, .3, 1
            halign: 'center'
            text_size: self.width, None
            size_hint_y: None
            height: (self.texture_size[1] + dp(6)) if self.text else 0
        Label:
            text: root.feedback
            font_size: sp(14)
            color: root.fb_color
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None
            size_hint_y: None
            height: dp(34)
        TextInput:
            id: ans
            multiline: False
            size_hint_y: None
            height: dp(56)
            font_size: sp(24)
            halign: 'center'
            hint_text: 'Type your answer'
            write_tab: False
            background_normal: ''
            background_active: ''
            background_disabled_normal: ''
            background_color: .13, .15, .3, 1
            foreground_color: 1, 1, 1, 1
            disabled_foreground_color: .5, .55, .75, 1
            hint_text_color: .5, .55, .75, 1
            cursor_color: .15, .88, .96, 1
            padding: dp(12), max(0, (self.height - self.line_height) / 2)
            on_text_validate: root.submit()
        BoxLayout:
            size_hint_y: None
            height: dp(54)
            spacing: dp(10)
            RBtn:
                text: 'Hint'
                size_hint_x: .38
                bg: .93, .62, .15, 1
                on_release: root.show_hint()
            RBtn:
                text: root.submit_text
                bg: .2, .78, .5, 1
                on_release: root.submit()
        BoxLayout:
            size_hint_y: None
            height: dp(42)
            spacing: dp(10)
            RBtn:
                text: 'Previous'
                height: dp(42)
                font_size: sp(14)
                rad: dp(14)
                bg: .17, .19, .36, 1
                on_release: root.go(-1)
            RBtn:
                text: 'Next'
                height: dp(42)
                font_size: sp(14)
                rad: dp(14)
                bg: .17, .19, .36, 1
                on_release: root.go(1)
    FloatLayout:
        id: fx

<LevelsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(14)
        spacing: dp(8)
        BoxLayout:
            size_hint_y: None
            height: dp(46)
            spacing: dp(8)
            RBtn:
                text: 'Back'
                size_hint_x: None
                width: dp(76)
                height: dp(44)
                font_size: sp(15)
                rad: dp(14)
                bg: .17, .19, .36, 1
                on_release: app.goto('home', 'right')
            Label:
                text: 'Select Level'
                font_size: sp(22)
                bold: True
        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)
            RBtn:
                text: '<'
                size_hint_x: None
                width: dp(64)
                height: dp(44)
                rad: dp(14)
                bg: .49, .36, 1, 1
                on_release: root.change_page(-1)
            Label:
                text: 'Levels ' + root.range_text
                font_size: sp(17)
                bold: True
                color: .8, .74, 1, 1
            RBtn:
                text: '>'
                size_hint_x: None
                width: dp(64)
                height: dp(44)
                rad: dp(14)
                bg: .49, .36, 1, 1
                on_release: root.change_page(1)
        ScrollView:
            do_scroll_x: False
            bar_width: dp(3)
            GridLayout:
                id: grid
                cols: 5
                spacing: dp(8)
                padding: 0, dp(4)
                size_hint_y: None
                height: self.minimum_height
        Label:
            text: root.status
            font_size: sp(13)
            color: 1, .82, .3, 1
            size_hint_y: None
            height: dp(20)
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            TextInput:
                id: jump_in
                multiline: False
                input_filter: 'int'
                hint_text: 'Go to level (1-2000)'
                font_size: sp(18)
                background_normal: ''
                background_active: ''
                background_color: .13, .15, .3, 1
                foreground_color: 1, 1, 1, 1
                hint_text_color: .5, .55, .75, 1
                cursor_color: .15, .88, .96, 1
                padding: dp(12), max(0, (self.height - self.line_height) / 2)
                on_text_validate: root.jump()
            RBtn:
                text: 'Go'
                size_hint_x: None
                width: dp(76)
                height: dp(48)
                rad: dp(14)
                bg: .2, .78, .5, 1
                on_release: root.jump()

<ProgressScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(14)
        spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(46)
            spacing: dp(8)
            RBtn:
                text: 'Back'
                size_hint_x: None
                width: dp(76)
                height: dp(44)
                font_size: sp(15)
                rad: dp(14)
                bg: .17, .19, .36, 1
                on_release: app.goto('home', 'right')
            Label:
                text: 'Your Progress'
                font_size: sp(22)
                bold: True
        Card:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(190)
            padding: dp(16)
            spacing: dp(4)
            Label:
                text: app.rank
                font_size: sp(24)
                bold: True
                color: .8, .74, 1, 1
            Label:
                text: str(int(app.points)) + ' points'
                font_size: sp(20)
                bold: True
                color: 1, .82, .3, 1
            Label:
                text: str(int(app.solved_n)) + ' / 2000 levels solved   (' + str(round(app.solved_n * 100.0 / 2000, 1)) + '%)'
                font_size: sp(15)
            Label:
                text: 'Hints used: ' + str(int(app.hints_used)) + '     Next level: ' + str(int(app.next_level))
                font_size: sp(14)
                color: .7, .74, .92, 1
            Bar:
                id: overall
                size_hint_y: None
                height: dp(14)
                col: .2, .78, .5, 1
        ScrollView:
            do_scroll_x: False
            bar_width: dp(3)
            BoxLayout:
                id: cats
                orientation: 'vertical'
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(14)
        spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(46)
            spacing: dp(8)
            RBtn:
                text: 'Back'
                size_hint_x: None
                width: dp(76)
                height: dp(44)
                font_size: sp(15)
                rad: dp(14)
                bg: .17, .19, .36, 1
                on_release: app.goto('home', 'right')
            Label:
                text: 'Settings'
                font_size: sp(22)
                bold: True
        Card:
            size_hint_y: None
            height: dp(66)
            padding: dp(18), dp(8)
            Label:
                text: 'Sound effects'
                font_size: sp(17)
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            Switch:
                size_hint_x: None
                width: dp(90)
                active: app.store.data['sound']
                on_active: app.set_opt('sound', self.active)
        Card:
            size_hint_y: None
            height: dp(66)
            padding: dp(18), dp(8)
            spacing: dp(10)
            Label:
                text: 'Volume'
                font_size: sp(17)
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                size_hint_x: .35
            Slider:
                min: 0
                max: 1
                value: app.store.data['volume']
                on_value: app.set_opt('volume', self.value)
        Card:
            size_hint_y: None
            height: dp(66)
            padding: dp(18), dp(8)
            Label:
                text: 'Animations'
                font_size: sp(17)
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            Switch:
                size_hint_x: None
                width: dp(90)
                active: app.store.data['anim']
                on_active: app.set_opt('anim', self.active)
        RBtn:
            text: 'Test sound'
            bg: .1, .62, .85, 1
            on_release: app.sfx.play('correct')
        RBtn:
            text: 'Reset all progress'
            bg: .85, .27, .35, 1
            on_release: app.confirm_reset()
        Widget:
        Label:
            text: 'Brain Boost 2000  v1.0\\n2,000 levels  |  10 points per level  |  progress saves automatically'
            font_size: sp(13)
            color: .6, .65, .85, 1
            halign: 'center'
            size_hint_y: None
            height: dp(44)
"""


# ---------------------------------------------------------------- screens
class HomeScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        app.refresh_stats()
        if not app.store.data["anim"]:
            return
        a = (Animation(font_size=sp(86), d=1.1, t="in_out_sine") +
             Animation(font_size=sp(80), d=1.1, t="in_out_sine"))
        a.repeat = True
        a.start(self.ids.logo2)
        self._anim = a
        for i, k in enumerate(("b1", "b2", "b3", "b4")):
            w = self.ids[k]
            w.opacity = 0
            Clock.schedule_once(
                lambda dt, w=w: Animation(opacity=1, d=0.35).start(w), 0.08 * i)

    def on_leave(self):
        if getattr(self, "_anim", None):
            self._anim.cancel(self.ids.logo2)
            self._anim = None
        for k in ("b1", "b2", "b3", "b4"):
            Animation.cancel_all(self.ids[k], "opacity")
            self.ids[k].opacity = 1 if not self.ids[k].disabled else 0.45


class GameScreen(Screen):
    level = NumericProperty(1)
    title_text = StringProperty("")
    cat_text = StringProperty("")
    q_text = StringProperty("")
    q_size = NumericProperty(sp(22))
    hint_text = StringProperty("")
    feedback = StringProperty("")
    fb_color = ListProperty([0.7, 0.75, 0.9, 1])
    mem_frac = NumericProperty(0)
    submit_text = StringProperty("Submit")
    phase = StringProperty("play")      # play | memory | solved
    p = None
    _mem_ev = None

    # ---- helpers
    def say(self, text, good=None):
        self.feedback = text
        self.fb_color = ([0.3, 0.9, 0.55, 1] if good is True else
                         [1, 0.4, 0.45, 1] if good is False else
                         [0.7, 0.75, 0.9, 1])

    def show_q(self, text, big=False):
        n = len(text)
        if big:
            size = sp(26) if ("\n" in text or n > 30) else sp(36)
        elif n < 60:
            size = sp(26)
        elif n < 140:
            size = sp(21)
        elif n < 250:
            size = sp(18)
        else:
            size = sp(16)
        self.q_size = size
        self.q_text = text

    def _cancel_mem(self):
        if self._mem_ev is not None:
            self._mem_ev.cancel()
            self._mem_ev = None

    def on_leave(self):
        self._cancel_mem()

    # ---- level loading
    def load_level(self, n):
        app = App.get_running_app()
        self._cancel_mem()
        n = max(1, min(TOTAL, int(n)))
        if n > len(app.bank):
            return
        self.level = n
        app.store.data["last"] = n
        self.p = p = app.bank[n - 1]
        self.title_text = "Level %d" % n
        self.cat_text = "%s   |   %s" % (p["cat"], difficulty_name(n))
        self.hint_text = ""
        self.ids.ans.text = ""
        self.mem_frac = 0
        self.submit_text = "Submit"
        self.phase = "play"
        self.say("Already solved - replaying is free." if n in app.store.solved
                 else "Solve it to earn 10 points!")
        if p["mem"]:
            self.phase = "memory"
            self.ids.ans.disabled = True
            self.show_q(p["mem"], big=True)
            self.say("Memorise it!  The question comes next.")
            self._t0 = time.perf_counter()
            self._mem_ev = Clock.schedule_interval(self._mem_tick, 1 / 30.0)
        else:
            self.ids.ans.disabled = False
            self.show_q(p["q"])
        card = self.ids.qcard
        if app.store.data["anim"]:
            card.opacity = 0
            Animation(opacity=1, d=0.35, t="out_quad").start(card)
        else:
            card.opacity = 1

    def _mem_tick(self, dt):
        el = time.perf_counter() - self._t0
        secs = self.p["secs"]
        self.mem_frac = max(0.0, 1.0 - el / secs)
        if el >= secs:
            self._cancel_mem()
            self.mem_frac = 0
            self.phase = "play"
            self.show_q(self.p["q"])
            self.ids.ans.disabled = False
            self.say("Now type your answer.")
            App.get_running_app().sfx.play("go")
            Clock.schedule_once(lambda dt: setattr(self.ids.ans, "focus", True), 0.1)

    # ---- actions
    def show_hint(self):
        app = App.get_running_app()
        if self.p is None:
            return
        self.hint_text = "Hint: " + self.p["hint"]
        app.sfx.play("hint")
        if self.level not in app.store.hinted:
            app.store.hinted.add(self.level)
            app.store.save()
            app.refresh_stats()
        if app.store.data["anim"]:
            lb = self.ids.hintlbl
            lb.opacity = 0
            Animation(opacity=1, d=0.4).start(lb)

    def go(self, delta):
        app = App.get_running_app()
        n = self.level + delta
        if n < 1 or n > TOTAL:
            return
        if n > app.store.reach():
            self.say("Locked! Solve more levels first (you can play up to level %d)."
                     % app.store.reach(), False)
            app.sfx.play("wrong")
            self.shake()
            return
        self.load_level(n)

    def submit(self):
        app = App.get_running_app()
        if self.p is None:
            return
        if self.phase == "solved":
            if self.level >= TOTAL:
                app.goto("progress")
            else:
                self.go(1)
            return
        if self.phase == "memory":
            self.say("Wait - memorise first!", False)
            return
        guess = norm(self.ids.ans.text)
        if not guess:
            self.say("Type an answer first.", False)
            self.shake()
            return
        if guess in self.p["a"]:
            self.on_correct()
        else:
            app.sfx.play("wrong")
            self.say("Not quite - try again or tap Hint.", False)
            self.shake()
            self.ids.ans.focus = True

    def on_correct(self):
        app = App.get_running_app()
        self.phase = "solved"
        self.ids.ans.disabled = True
        self.ids.ans.focus = False
        first = self.level not in app.store.solved
        if first:
            app.store.solved.add(self.level)
            app.store.save()
            app.refresh_stats()
            self.say("Correct!  +%d points" % POINTS_PER_LEVEL, True)
        else:
            self.say("Correct! (already counted)", True)
        self.submit_text = "Finish" if self.level >= TOTAL else "Next Level"
        if self.level >= TOTAL and first:
            self.say("You completed all 2000 levels! Legend!", True)
        app.sfx.play("win" if (first and self.level % 25 == 0) or self.level == TOTAL
                     else "correct")
        if app.store.data["anim"]:
            card = self.ids.qcard
            base = list(card.bg)
            (Animation(bg=[0.1, 0.5, 0.32, 1], d=0.18) +
             Animation(bg=base, d=0.6)).start(card)
            if first:
                self.float_points()
            self.confetti(36 if self.level % 25 == 0 else 20)

    # ---- effects
    def shake(self):
        if not App.get_running_app().store.data["anim"]:
            return
        w = self.ids.ans
        ox = w.x
        Animation.cancel_all(w, "x")
        (Animation(x=ox - dp(14), d=0.05) + Animation(x=ox + dp(14), d=0.07) +
         Animation(x=ox - dp(9), d=0.06) + Animation(x=ox, d=0.05)).start(w)

    def float_points(self):
        fx = self.ids.fx
        lb = Label(text="+%d" % POINTS_PER_LEVEL, font_size=sp(48), bold=True,
                   color=(1, 0.82, 0.3, 1), size_hint=(None, None),
                   size=(dp(160), dp(70)))
        lb.center = (self.center_x, self.height * 0.62)
        fx.add_widget(lb)
        a = Animation(y=lb.y + dp(140), opacity=0, d=1.3, t="out_quad")
        a.bind(on_complete=lambda anim, w: fx.remove_widget(w))
        a.start(lb)

    def confetti(self, n):
        fx = self.ids.fx
        cols = [(0.49, 0.36, 1, 1), (0.15, 0.88, 0.96, 1), (1, 0.82, 0.3, 1),
                (0.3, 0.9, 0.55, 1), (1, 0.4, 0.55, 1)]
        cx, cy = self.center_x, self.height * 0.58
        for _ in range(n):
            s = random.uniform(dp(6), dp(12))
            d = Dot(size=(s, s), size_hint=(None, None), pos=(cx, cy),
                    col=random.choice(cols))
            fx.add_widget(d)
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(dp(80), dp(230))
            a = Animation(x=cx + math.cos(ang) * dist,
                          y=cy + math.sin(ang) * dist + dp(30),
                          opacity=0, d=random.uniform(0.7, 1.2), t="out_quad")
            a.bind(on_complete=lambda anim, w: fx.remove_widget(w))
            a.start(d)


class LevelsScreen(Screen):
    page = NumericProperty(0)
    range_text = StringProperty("")
    status = StringProperty("")

    def on_pre_enter(self):
        app = App.get_running_app()
        self.page = (max(1, int(app.store.data.get("last", 1))) - 1) // PAGE
        self.status = ""
        self.build()

    def change_page(self, d):
        self.page = max(0, min(TOTAL // PAGE - 1, self.page + d))
        App.get_running_app().sfx.play("tap")
        self.build()

    def build(self):
        app = App.get_running_app()
        grid = self.ids.grid
        grid.clear_widgets()
        start = self.page * PAGE + 1
        end = min(TOTAL, start + PAGE - 1)
        self.range_text = "%d - %d" % (start, end)
        reach = app.store.reach()
        nxt = app.store.next_unsolved()
        for n in range(start, end + 1):
            if n in app.store.solved:
                bg = [0.16, 0.6, 0.4, 1]
            elif n == nxt:
                bg = [0.1, 0.62, 0.85, 1]
            elif n <= reach:
                bg = [0.38, 0.3, 0.85, 1]
            else:
                bg = [0.14, 0.15, 0.27, 1]
            b = RBtn(text=str(n), bg=bg, rad=dp(14), height=dp(54),
                     font_size=sp(16), disabled=(n > reach))
            b.bind(on_release=lambda w, n=n: app.open_level(n))
            grid.add_widget(b)

    def jump(self):
        app = App.get_running_app()
        txt = self.ids.jump_in.text.strip()
        if not txt.isdigit() or not (1 <= int(txt) <= TOTAL):
            self.status = "Enter a level number from 1 to %d." % TOTAL
            return
        n = int(txt)
        if n > app.store.reach():
            self.page = (n - 1) // PAGE
            self.build()
            self.status = "Level %d is locked. You can play up to level %d." % (
                n, app.store.reach())
            return
        app.open_level(n)


class ProgressScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        app.refresh_stats()
        bar = self.ids.overall
        bar.value = 0
        Animation(value=app.solved_n / float(TOTAL), d=0.8, t="out_quad").start(bar)
        box = self.ids.cats
        box.clear_widgets()
        solved = app.store.solved
        colors = [(0.49, 0.36, 1, 1), (0.15, 0.88, 0.96, 1), (1, 0.62, 0.2, 1),
                  (1, 0.4, 0.55, 1), (0.3, 0.9, 0.55, 1), (0.95, 0.85, 0.3, 1),
                  (0.7, 0.5, 1, 1), (0.2, 0.7, 0.95, 1)]
        for i, cat in enumerate(CATS):
            total = TOTAL // len(CATS)
            done = sum(1 for n in solved if (n - 1) % len(CATS) == i)
            row = BoxLayout(orientation="vertical", size_hint_y=None,
                            height=dp(46), spacing=dp(4))
            top = BoxLayout(size_hint_y=None, height=dp(22))
            top.add_widget(left_label(cat, font_size=sp(15), bold=True))
            top.add_widget(Label(text="%d / %d" % (done, total), font_size=sp(14),
                                 color=(0.7, 0.74, 0.92, 1), size_hint_x=None,
                                 width=dp(90)))
            b = Bar(size_hint_y=None, height=dp(12), col=list(colors[i]))
            row.add_widget(top)
            row.add_widget(b)
            box.add_widget(row)
            Animation(value=done / float(total), d=0.8, t="out_quad").start(b)


class SettingsScreen(Screen):
    pass


# -------------------------------------------------------------------- app
class BrainBoostApp(App):
    points = NumericProperty(0)
    solved_n = NumericProperty(0)
    hints_used = NumericProperty(0)
    next_level = NumericProperty(1)
    rank = StringProperty("Rookie")
    play_text = StringProperty("PLAY")
    load_text = StringProperty("Loading ..")
    ready = BooleanProperty(False)

    def build(self):
        self.title = "Brain Boost 2000"
        Window.softinput_mode = "below_target"
        self.bank = []
        self._popup = None
        self.store = Store(os.path.join(self.user_data_dir, "save.json"))
        self.sfx = Sfx(os.path.join(self.user_data_dir, "sfx"), self.store)
        Builder.load_string(KV)
        self.sm = ScreenManager(transition=SlideTransition(duration=0.22))
        for cls, name in ((HomeScreen, "home"), (LevelsScreen, "levels"),
                          (GameScreen, "game"), (ProgressScreen, "progress"),
                          (SettingsScreen, "settings")):
            self.sm.add_widget(cls(name=name))
        Window.bind(on_keyboard=self.on_key)
        self.refresh_stats()
        return self.sm

    # ---- puzzle loading (chunked so the UI never freezes)
    def on_start(self):
        self._gen = iter_levels()
        Clock.schedule_interval(self._load_chunk, 0)

    def _load_chunk(self, dt):
        t0 = time.perf_counter()
        try:
            while time.perf_counter() - t0 < 0.012:
                self.bank.append(next(self._gen))
        except StopIteration:
            self.ready = True
            self.load_text = ""
            self.refresh_stats()
            return False
        self.load_text = "Preparing ..  %d%%" % (len(self.bank) * 100 // TOTAL)

    # ---- stats
    def refresh_stats(self):
        s = self.store
        self.solved_n = len(s.solved)
        self.points = POINTS_PER_LEVEL * len(s.solved)
        self.hints_used = len(s.hinted)
        self.next_level = s.next_unsolved()
        self.play_text = "PLAY   -   Level %d" % self.next_level
        rank = RANKS[0][1]
        for need, name in RANKS:
            if self.solved_n >= need:
                rank = name
        self.rank = rank

    def set_opt(self, key, value):
        self.store.data[key] = value
        self.store.save()

    # ---- navigation
    def goto(self, name, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = name

    def play(self):
        if self.ready:
            self.open_level(self.store.next_unsolved())

    def open_levels(self):
        self.goto("levels")

    def open_level(self, n):
        if not self.ready and n > len(self.bank):
            return
        self.sfx.play("go")
        self.sm.get_screen("game").load_level(n)
        self.goto("game")

    def back_to_levels(self):
        self.goto("levels", "right")

    def on_key(self, window, key, *args):
        if key == 27:            # Android back button / Esc
            if self._popup is not None:
                self._popup.dismiss()
                return True
            cur = self.sm.current
            if cur == "home":
                return False
            if cur == "game":
                self.goto("levels", "right")
            else:
                self.goto("home", "right")
            return True
        return False

    # ---- reset dialog
    def confirm_reset(self):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        lb = Label(text="This erases ALL solved levels and points.\nThis cannot be undone.",
                   halign="center", font_size=sp(15))
        lb.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        pop = Popup(title="Reset progress?", content=box, size_hint=(0.88, None),
                    height=dp(240), separator_color=(0.49, 0.36, 1, 1))
        cancel = RBtn(text="Cancel", bg=[0.3, 0.33, 0.55, 1], height=dp(48))
        ok = RBtn(text="Reset", bg=[0.85, 0.27, 0.35, 1], height=dp(48))
        cancel.bind(on_release=lambda *a: pop.dismiss())

        def do_reset(*a):
            self.store.reset()
            self.refresh_stats()
            pop.dismiss()

        ok.bind(on_release=do_reset)
        row.add_widget(cancel)
        row.add_widget(ok)
        box.add_widget(lb)
        box.add_widget(row)
        pop.bind(on_dismiss=lambda *a: setattr(self, "_popup", None))
        self._popup = pop
        pop.open()

    # ---- lifecycle (auto-save)
    def on_pause(self):
        self.store.save()
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        self.store.save()


if __name__ == "__main__":
    BrainBoostApp().run()
