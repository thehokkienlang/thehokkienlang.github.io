# Learn pages: drafted text changes for review

Status: **draft for Haru's review. Nothing in this file is on the site.**
Every example below reuses a word, reading or tone that is already in the current guides;
no new readings, tones or glosses are introduced. Tick or amend each item, then it can be
applied to the English page and translated for the two Chinese pages.

Already done in code (no teaching text changed): the Learn index now has a "Start here"
path and a "Reference" group with one sentence per page, each guide ends with a Next link,
and the Learn menu lists the guides in reading order.

---

## 1. Introduction: explain how a block is built (new section, before "The alphabets")

**Problem.** The page opens with "41 alphabets (jamo)" and their sorting order. A reader who
has never seen Hangul is not told that each block is one syllable made of smaller letters.

**Draft: "How a syllable block works"**

> Tangliengim is written in blocks. **One block is one syllable**, and each block is built
> from two or three letters:
>
> | Block | Letters | Sound |
> |---|---|---|
> | 김 | ㄱ + ㅣ + ㅁ | k + i + m → *kim* |
> | 장 | ㅈ + ㅏ + ㅇ | j + a + ng → *jang* |
> | 빻 | ㅃ + ㅏ + ㅎ | b + a + h → *bah* |
>
> Read each block from the top left: first the **initial** consonant, then the **vowel**,
> then, if there is one, the **final** consonant underneath. The tables below go through
> these three positions in turn.
>
> If you can read Korean, the blocks will look familiar, but the sounds are Hokkien: read
> them with the values given here, not the Korean ones.

- [ ] Approve as drafted
- [ ] The three example blocks (김 from 김죠, 장, 빻) are the ones you want
- Notes:

## 2. Introduction: wording of the letters paragraph

**Problem.** "41 alphabets" should be "41 letters"; the sorting order is reference detail
that a beginner does not need first.

**Draft**

> Tangliengim has 41 letters (jamo): 19 initial consonants and 22 vowels. Eight of the
> consonants can also close a syllable as a final, and two of those, ㄹ and ㅎ, can combine
> as ㅀ. ㅉ and ᅟힻ are used only in foreign words.
>
> *(Move the alphabetical order and the order of finals into a collapsed "Alphabetical
> order" note, or to the Spelling guidelines.)*

- [ ] Approve; counts are right (19 initials + 22 vowels = 41; finals ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅇ ㅎ plus ㅀ)
- [ ] Where should the alphabetical order go? ☐ collapsed note here ☐ Spelling guidelines
- Notes:

## 3. Introduction: tones in plain words

**Correction to the audit.** The tone table already has a recording of 덩 in each of the
five tones, so a "listening row" exists. What is missing is a description for readers who
do not know Mandarin Pinyin.

**Draft: add a "Sounds like" column** (pitch shapes taken from the tone values already
published on the Romanisation page: 44, 53, 21, 214, 22)

| Tone | Mark | Sounds like | Pinyin comparison (keep) |
|---|---|---|---|
| 1 High | ˆ | stays high and level | ≈ 1st tone |
| 2 Falling | ˋ | starts high and drops | ≈ 4th tone |
| 3 Low | (unmarked) | stays low, sinking slightly | ≈ 3rd tone |
| 4 Rising | ˊ | dips, then climbs | ≈ 2nd tone |
| 5 Mid | ˉ | level, in the middle of your voice | between 1st and 3rd |

- [ ] Approve the five descriptions
- Notes:

**Draft: replace the dense "modes" paragraph** (currently stated twice, under Tones and
under Typing) with one statement and one example:

> Text can be written two ways, and one text sticks to one way throughout:
>
> - **With tone marks**, as on this site. Here a syllable without a mark is Low tone (or
>   neutral, if it follows an apostrophe).
> - **Without tone marks**, as in everyday typing. Here no syllable shows its tone at all,
>   so an unmarked syllable tells you nothing about its tone.
>
> | With tone marks | Without |
> |---|---|
> | 릐ˋ 今仔日 食飽’쀄? | 릐 긴아띧 쟣바'쀄? |

- [ ] Approve (the example pair is the one already under "Typing Tangliengim")
- Notes:

## 4. Introduction: "Typing Tangliengim"

**Problems.** It only covers the Korean keyboard on Windows 11, and never mentions the
site's own keyboard or the Android keyboard. It also says tones are omitted "since Unicode
does not currently support tone diacritics", while this site displays and types tone marks.

**Draft**

> ### The easiest way: the TLI keyboard
> The [Hokkien IME](/ime/) on this site types Tangliengim in your browser, with Hanri
> candidates, tone marks and Lomari, and nothing to install. On Android, the TLI keyboard
> does the same in any app; its download link is on the IME page.
>
> ### Using an ordinary Korean keyboard
> You can also type with the Korean keyboard built into your computer or phone. It has no
> keys for the tone marks, so text typed this way is written without tones.
> *(then the existing Windows 11 steps, the ᅟᅡᆽ / ᅟᅣᆽ shorthand, and the Old Hangul keyboard)*

- [ ] Approve
- [ ] Question: is "the Korean keyboard has no keys for the tone marks" the accurate reason
      to give instead of the Unicode sentence? If not, what should it say?
- [ ] Should the Android keyboard be mentioned while it is a test build?
- Notes:

## 5. Tone sandhi: plain-language glosses

The opening rule is clear. These terms appear later without explanation; proposed glosses,
added in brackets at first use, leaving your examples untouched:

| Term now | Proposed first-use wording |
|---|---|
| N / X | "N (behaves like a noun) / X (everything else)", and move the legend above the first example |
| "accusative position" | "when it is the object of the verb (the one the action is done to)" |
| "postposition" | "a word attached after a noun, such as –래 ‘in’" |
| "grammaticalisation of the Chinese character 共" | "originally the character 共, now used as a grammar word" |
| "checked tone" | "a syllable ending in -p, -t, -k or -h" |
| The sandhi diagram | add one sentence before it: "Read each arrow as ‘becomes’: for example High becomes Mid." |

- [ ] Approve all / strike any you want kept technical
- [ ] Is the gloss for "checked tone" right for TLI (finals ㅂ ㄷ ㄱ ㅎ)?
- Notes:

## 6. Spelling and Romanisation: say who they are for

**Draft: one line at the top of each**

> *Spelling guidelines:* This is a reference page for readers who already read Tangliengim
> and want to know why a word is spelled the way it is. New here? Start with the
> [Introduction](/learn/introduction/).
>
> *Romanisation:* This page is for readers who know POJ or Tâi-lô and want to see how
> Lomari differs. You do not need it to start reading.

- [ ] Approve
- Notes:

## 7. Later: splitting the Introduction into short lessons

Not drafted yet, because it changes page addresses in three languages and should follow
the text decisions above. Proposed lessons, each one screen or two long:

1. What Tangliengim is, and how a block works (items 1 and 2 above)
2. Initial consonants
3. Vowels
4. Final consonants
5. Tones (item 3 above), ending with the short tone sandhi teaser
6. Your first phrases (the existing "Everyday phrases" table)
7. Typing (item 4 above)

The current address `/learn/introduction/` would stay as lesson 1, with its in-page links
redirecting to the new pages.

- [ ] Go ahead after items 1–6 are settled
- [ ] Keep it as one page
- Notes:
