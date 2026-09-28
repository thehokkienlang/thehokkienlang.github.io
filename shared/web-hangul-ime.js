const TangliengimHangulIme = (() => {
  const L_TABLE = [...Array(19)].map((_, index) => String.fromCodePoint(0x1100 + index));
  const V_TABLE = [...Array(21)].map((_, index) => String.fromCodePoint(0x1161 + index));
  const T_TABLE = ["", ...[...Array(27)].map((_, index) => String.fromCodePoint(0x11a8 + index))];
  const L_INDEX = Object.fromEntries(L_TABLE.map((char, index) => [char, index]));
  const V_INDEX = Object.fromEntries(V_TABLE.map((char, index) => [char, index]));
  const T_INDEX = Object.fromEntries(T_TABLE.map((char, index) => [char, index]));

  const KEY_TO_JAMO = {
    r: "ㄱ", R: "ㄲ", s: "ㄴ", e: "ㄷ", E: "ㄸ", f: "ㄹ",
    a: "ㅁ", q: "ㅂ", Q: "ㅃ", t: "ㅅ", d: "ㅇ",
    w: "ㅈ", W: "ㅉ", c: "ㅊ", z: "ㅋ", x: "ㅌ", v: "ㅍ", g: "ㅎ", G: "ㆆ",
    k: "ㅏ", o: "ㅐ", i: "ㅑ", j: "ㅓ", p: "ㅔ", P: "ㅖ",
    u: "ㅕ", h: "ㅗ", y: "ㅛ", n: "ㅜ", b: "ㅠ", m: "ㅡ", l: "ㅣ",
  };
  const SHIFT_PRESERVED_KEYS = new Set(["R", "E", "Q", "W", "P", "G"]);

  const COMPAT_TO_L = {
    "ㄱ": "ᄀ", "ㄲ": "ᄁ", "ㄴ": "ᄂ", "ㄷ": "ᄃ", "ㄸ": "ᄄ", "ㄹ": "ᄅ",
    "ㅁ": "ᄆ", "ㅂ": "ᄇ", "ㅃ": "ᄈ", "ㅅ": "ᄉ", "ㅇ": "ᄋ",
    "ㅈ": "ᄌ", "ㅉ": "ᄍ", "ㅊ": "ᄎ", "ㅋ": "ᄏ", "ㅌ": "ᄐ", "ㅍ": "ᄑ", "ㅎ": "ᄒ",
    "ㆆ": "ᅙ",
  };
  const COMPAT_TO_V = {
    "ㅏ": "ᅡ", "ㅐ": "ᅢ", "ㅑ": "ᅣ", "ㅓ": "ᅥ", "ㅔ": "ᅦ",
    "ㅕ": "ᅧ", "ㅖ": "ᅨ", "ㅗ": "ᅩ", "ㅛ": "ᅭ", "ㅜ": "ᅮ", "ㅠ": "ᅲ",
    "ㅡ": "ᅳ", "ㅣ": "ᅵ", "ㅢ": "ᅴ",
  };
  // ㅅ/ㅊ are onset-only; ㅈ is handled as a ㅏ/ㅑ special-medial shortcut.
  const COMPAT_TO_T = {
    "ㄱ": "ᆨ", "ㄴ": "ᆫ", "ㄷ": "ᆮ", "ㄹ": "ᆯ", "ㅁ": "ᆷ",
    "ㅂ": "ᆸ", "ㅇ": "ᆼ", "ㅎ": "ᇂ",
  };
  const T_TO_L = {
    "ᆨ": "ᄀ", "ᆫ": "ᄂ", "ᆮ": "ᄃ", "ᆯ": "ᄅ", "ᆷ": "ᄆ",
    "ᆸ": "ᄇ", "ᆼ": "ᄋ", "ᇂ": "ᄒ",
  };
  const L_TO_COMPAT = Object.fromEntries(Object.entries(COMPAT_TO_L).map(([key, value]) => [value, key]));
  const V_TO_COMPAT = Object.fromEntries(Object.entries(COMPAT_TO_V).map(([key, value]) => [value, key]));
  Object.assign(V_TO_COMPAT, {
    "ᅪ": "ㅘ",
    "ᅫ": "ㅙ",
    "ᅬ": "ㅚ",
    "ᅰ": "ㅞ",
    "ᅱ": "ㅟ",
    "ᅴ": "ㅢ",
  });
  const T_TO_COMPAT = Object.fromEntries(Object.entries(COMPAT_TO_T).map(([key, value]) => [value, key]));
  T_TO_COMPAT["ᆶ"] = "ㅀ";

  const V_COMBINE = {
    "ᅩᅡ": "ᅪ",
    "ᅩᅢ": "ᅫ",
    "ᅩᅵ": "ᅬ",
    "ᅮᅦ": "ᅰ",
    "ᅮᅵ": "ᅱ",
    "ᅳᅵ": "ᅴ",
  };
  const NATIVE_V_COMBINE = { "ᅡᅮ": "ᅷ", "ᅣᅮ": "ᆤ" };
  const T_COMBINE = { "ᆯᇂ": "ᆶ" };
  const T_SPLIT = { "ᆶ": ["ᆯ", "ᇂ"] };
  const SPECIAL_MEDIALS = new Set(["ᅷ", "ᆤ", "ힻ"]);
  const FINAL_J_SHORTCUT_MEDIALS = { "ᅡ": "ᅷ", "ᅣ": "ᆤ" };
  const DISALLOWED_FINAL_TO_COMPAT = { "ᆺ": "ㅅ", "ᆽ": "ㅈ", "ᆾ": "ㅊ" };
  const SPECIAL_MEDIAL_BACKSPACE_BASE = {
    "ᅷ": "ᅡ",
    "ᆤ": "ᅣ",
    "ힻ": "ᅳ",
  };
  const HANGUL_CHOSEONG_FILLER = "\u115f";
  const NATIVE_SPECIAL_MEDIAL_ONSET = { "ᅷ": HANGUL_CHOSEONG_FILLER, "ᆤ": "ᄋ" };
  const TONE_MARKS = { 1: "ˆ", 2: "ˋ", 4: "ˊ", 5: "ˉ" };
  const TONE_INPUT = { "ˆ": "1", "ꞈ": "1", "ˋ": "2", "`": "2", "ˎ": "2", "ˊ": "4", "ˏ": "4", "ˉ": "5", "ˍ": "5" };
  const NATIVE_VOWEL_INPUT = {
    "ᅡ": ["ㅏ"], "ᅢ": ["ㅐ"], "ᅣ": ["ㅑ"], "ᅥ": ["ㅓ"], "ᅦ": ["ㅔ"],
    "ᅧ": ["ㅕ"], "ᅨ": ["ㅖ"], "ᅩ": ["ㅗ"], "ᅪ": ["ㅗ", "ㅏ"],
    "ᅫ": ["ㅗ", "ㅐ"], "ᅬ": ["ㅗ", "ㅣ"], "ᅭ": ["ㅛ"], "ᅮ": ["ㅜ"],
    "ᅰ": ["ㅜ", "ㅔ"], "ᅱ": ["ㅜ", "ㅣ"], "ᅲ": ["ㅠ"], "ᅳ": ["ㅡ"],
    "ᅴ": ["ㅡ", "ㅣ"], "ᅵ": ["ㅣ"],
  };
  const NATIVE_COMPAT_VOWEL_INPUT = {
    "ㅘ": ["ㅗ", "ㅏ"], "ㅙ": ["ㅗ", "ㅐ"], "ㅚ": ["ㅗ", "ㅣ"],
    "ㅞ": ["ㅜ", "ㅔ"], "ㅟ": ["ㅜ", "ㅣ"], "ㅢ": ["ㅡ", "ㅣ"],
  };
  const NATIVE_SPECIAL_VOWEL_INPUT = { "ᅷ": ["ㅏ", "ㅜ"], "ᆤ": ["ㅑ", "ㅜ"] };
  const NATIVE_FINAL_INPUT = {
    "ᆨ": ["ㄱ"], "ᆩ": ["ㄲ"], "ᆪ": ["ㄱ", "ㅅ"], "ᆫ": ["ㄴ"],
    "ᆬ": ["ㄴ", "ㅈ"], "ᆭ": ["ㄴ", "ㅎ"], "ᆮ": ["ㄷ"], "ᆯ": ["ㄹ"],
    "ᆰ": ["ㄹ", "ㄱ"], "ᆱ": ["ㄹ", "ㅁ"], "ᆲ": ["ㄹ", "ㅂ"],
    "ᆳ": ["ㄹ", "ㅅ"], "ᆴ": ["ㄹ", "ㅌ"], "ᆵ": ["ㄹ", "ㅍ"],
    "ᆶ": ["ㄹ", "ㅎ"], "ᆷ": ["ㅁ"], "ᆸ": ["ㅂ"], "ᆹ": ["ㅂ", "ㅅ"],
    "ᆺ": ["ㅅ"], "ᆻ": ["ㅅ", "ㅅ"], "ᆼ": ["ㅇ"], "ᆽ": ["ㅈ"],
    "ᆾ": ["ㅊ"], "ᆿ": ["ㅋ"], "ᇀ": ["ㅌ"], "ᇁ": ["ㅍ"], "ᇂ": ["ㅎ"],
  };

  function normalizeApostrophes(value) {
    return String(value ?? "").replaceAll("'", "’");
  }

  function containsNativeKoreanInput(value) {
    return /[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]/u.test(String(value || ""));
  }

  function nativeKoreanInputUnits(value) {
    const units = [];
    const compose = (items) => {
      for (const text of items) units.push({ text, compose: true });
    };

    for (const char of String(value || "")) {
      if (char in COMPAT_TO_L || char in COMPAT_TO_V) {
        compose([char]);
        continue;
      }
      if (char in NATIVE_COMPAT_VOWEL_INPUT) {
        compose(NATIVE_COMPAT_VOWEL_INPUT[char]);
        continue;
      }
      if (char in L_TO_COMPAT) {
        compose([L_TO_COMPAT[char]]);
        continue;
      }
      if (char in NATIVE_VOWEL_INPUT) {
        compose(NATIVE_VOWEL_INPUT[char]);
        continue;
      }
      if (char in NATIVE_SPECIAL_VOWEL_INPUT) {
        compose(NATIVE_SPECIAL_VOWEL_INPUT[char]);
        continue;
      }
      if (char in NATIVE_FINAL_INPUT) {
        compose(NATIVE_FINAL_INPUT[char]);
        continue;
      }

      const code = char.codePointAt(0);
      const offset = code - 0xac00;
      if (offset >= 0 && offset < 11172) {
        const initial = L_TABLE[Math.floor(offset / 588)];
        const medial = V_TABLE[Math.floor((offset % 588) / 28)];
        const final = T_TABLE[offset % 28];
        const initialInput = L_TO_COMPAT[initial];
        const medialInput = NATIVE_VOWEL_INPUT[medial];
        if (initialInput && medialInput) {
          compose([initialInput, ...medialInput, ...(NATIVE_FINAL_INPUT[final] || [])]);
          continue;
        }
      }
      units.push({ text: char, compose: false });
    }
    return units;
  }

  function nativeStandaloneVowelAt(value, index = 0) {
    const text = String(value || "");
    const char = text.slice(index, index + 1);
    if (!char) return null;
    if (char === HANGUL_CHOSEONG_FILLER && text[index + 1] in NATIVE_SPECIAL_VOWEL_INPUT) {
      return { inputs: NATIVE_SPECIAL_VOWEL_INPUT[text[index + 1]], length: 2 };
    }
    if (text[index - 1] === HANGUL_CHOSEONG_FILLER && char in NATIVE_SPECIAL_VOWEL_INPUT) {
      return { inputs: NATIVE_SPECIAL_VOWEL_INPUT[char], length: 2 };
    }
    if (char in COMPAT_TO_V) return { inputs: [char], length: char.length };
    if (char in NATIVE_COMPAT_VOWEL_INPUT) {
      return { inputs: NATIVE_COMPAT_VOWEL_INPUT[char], length: char.length };
    }
    if (char in NATIVE_VOWEL_INPUT) return { inputs: NATIVE_VOWEL_INPUT[char], length: char.length };
    if (char in NATIVE_SPECIAL_VOWEL_INPUT) {
      return { inputs: NATIVE_SPECIAL_VOWEL_INPUT[char], length: char.length };
    }

    const code = char.codePointAt(0);
    const offset = code - 0xac00;
    if (offset < 0 || offset >= 11172) return null;
    const initial = L_TABLE[Math.floor(offset / 588)];
    const medial = V_TABLE[Math.floor((offset % 588) / 28)];
    if (initial !== "ᄋ" || T_TABLE[offset % 28]) return null;
    const inputs = NATIVE_VOWEL_INPUT[medial];
    return inputs ? { inputs, initial: "ㅇ", length: char.length } : null;
  }

  function nativeStandaloneVowelInputs(...vowels) {
    return vowels.flatMap((vowel) => [
      ...(vowel?.initial ? [vowel.initial] : []),
      ...(vowel?.inputs || []),
    ]);
  }

  function composeNativeVowelInputs(inputs) {
    const composer = new Composer();
    for (const input of inputs) composer.processNativeCompat(input);
    composer.commit();
    const result = [...composer.text()];
    if (result.length === 1 && (
      isVowelJamo(result[0]) ||
      result[0] in COMPAT_TO_V ||
      result[0] in NATIVE_COMPAT_VOWEL_INPUT
    )) return result.join("");
    if (
      result.length === 2 &&
      (result[0] === HANGUL_CHOSEONG_FILLER || isInitialJamo(result[0])) &&
      SPECIAL_MEDIALS.has(result[1])
    ) {
      return result.join("");
    }
    return "";
  }

  const INITIAL_KEY_TO_L = Object.fromEntries(
    Object.entries(KEY_TO_JAMO)
      .filter(([, jamo]) => jamo in COMPAT_TO_L)
      .map(([key, jamo]) => [key, COMPAT_TO_L[jamo]])
  );
  const HOKKIEN_SEQUENCE_MAP = {};
  for (const [key, initial] of Object.entries(INITIAL_KEY_TO_L)) {
    HOKKIEN_SEQUENCE_MAP[`${key}mp`] = `${initial}ힻ`;
    HOKKIEN_SEQUENCE_MAP[`${key}kn`] = `${initial}ᅷ`;
    HOKKIEN_SEQUENCE_MAP[`${key}in`] = `${initial}ᆤ`;
  }
  Object.assign(HOKKIEN_SEQUENCE_MAP, {
    mp: `${HANGUL_CHOSEONG_FILLER}ힻ`,
    kn: `${HANGUL_CHOSEONG_FILLER}ᅷ`,
    in: `${HANGUL_CHOSEONG_FILLER}ᆤ`,
    mdk: "ᅙᅡ",
  });
  const MAX_SEQUENCE_LENGTH = Math.max(...Object.keys(HOKKIEN_SEQUENCE_MAP).map((key) => key.length));

  function normalizeKeyboardChar(char) {
    if (/^[A-Z]$/.test(char) && !SHIFT_PRESERVED_KEYS.has(char)) return char.toLowerCase();
    return char;
  }

  function keyboardGuideOutput(char) {
    const normalized = normalizeKeyboardChar(char);
    if ("1245".includes(normalized)) {
      return TONE_MARKS[normalized] || "";
    }
    return KEY_TO_JAMO[normalized] || "";
  }

  function composeSyllable(initial, medial, final = "") {
    if (initial in L_INDEX && medial in V_INDEX && final in T_INDEX) {
      return String.fromCodePoint(0xac00 + (L_INDEX[initial] * 21 + V_INDEX[medial]) * 28 + T_INDEX[final]);
    }
    return `${initial}${medial}${final}`;
  }

  function normalizeDisallowedFinalInputText(value) {
    let output = "";
    for (const char of String(value ?? "")) {
      const code = char.codePointAt(0);
      const offset = code - 0xac00;
      const final = offset >= 0 && offset < 11172 ? T_TABLE[offset % 28] : "";
      if (!(final in DISALLOWED_FINAL_TO_COMPAT)) {
        output += char;
        continue;
      }
      const medial = V_TABLE[Math.floor((offset % 588) / 28)];
      if (final === "ᆽ" && medial in FINAL_J_SHORTCUT_MEDIALS) {
        output += char;
        continue;
      }
      output += `${String.fromCodePoint(code - T_INDEX[final])}${DISALLOWED_FINAL_TO_COMPAT[final]}`;
    }
    return output;
  }

  function canBeFinal(compat) {
    return compat in COMPAT_TO_T;
  }

  function isInitialJamo(char) {
    return char in L_INDEX || char === "ᅙ";
  }

  function isVowelJamo(char) {
    return char in V_INDEX || SPECIAL_MEDIALS.has(char);
  }

  function isHangulishForTone(char) {
    if (!char) return false;
    const code = char.codePointAt(0);
    return (
      (code >= 0xac00 && code <= 0xd7a3) ||
      (code >= 0x3130 && code <= 0x318f) ||
      (code >= 0x1100 && code <= 0x11ff) ||
      SPECIAL_MEDIALS.has(char)
    );
  }

  function normalizeReadingBase(value) {
    return [...String(value || "")]
      .filter((char) => !"12345ˆˋ`ˊˉꞈˎˏˍ".includes(char))
      .join("");
  }

  function normalizeReadingToneKey(value) {
    return [...normalizeApostrophes(value)]
      .map((char) => TONE_INPUT[char] || char)
      .join("")
      .normalize("NFC");
  }

  function atomicHangulClusterEndAt(text, start) {
    if (start < 0 || start >= text.length) return null;
    const char = text[start];
    if (!(isInitialJamo(char) || char === HANGUL_CHOSEONG_FILLER)) return null;
    if (!isVowelJamo(text[start + 1])) return null;
    let end = start + 2;
    while (end < text.length && text[end] in T_INDEX && text[end] !== "") end += 1;
    return end;
  }

  function atomicHangulClusterBoundsAt(text, position) {
    const pos = Math.max(0, Math.min(position, text.length));
    for (let start = Math.max(0, pos - 4); start <= Math.min(pos, text.length - 1); start += 1) {
      const end = atomicHangulClusterEndAt(text, start);
      if (end !== null && start < pos && pos < end) return [start, end];
    }
    return null;
  }

  function atomicHangulClusterBoundsEndingAt(text, position) {
    const pos = Math.max(0, Math.min(position, text.length));
    for (let start = Math.max(0, pos - 4); start < pos; start += 1) {
      const end = atomicHangulClusterEndAt(text, start);
      if (end === pos) return [start, end];
    }
    return null;
  }

  function snapAtomicCursor(text, position) {
    const bounds = atomicHangulClusterBoundsAt(text, position);
    return bounds ? bounds[1] : Math.max(0, Math.min(position, text.length));
  }

  function normalizeAtomicSelection(text, start, end) {
    let selectionStart = Math.max(0, Math.min(start, text.length));
    let selectionEnd = Math.max(selectionStart, Math.min(end, text.length));
    if (selectionStart === selectionEnd) {
      const cursor = snapAtomicCursor(text, selectionStart);
      return [cursor, cursor];
    }
    const startBounds = atomicHangulClusterBoundsAt(text, selectionStart);
    const endBounds = atomicHangulClusterBoundsAt(text, selectionEnd);
    if (startBounds) selectionStart = startBounds[0];
    if (endBounds) selectionEnd = endBounds[1];
    return [selectionStart, selectionEnd];
  }

  class Composer {
    constructor({ shouldAutocorrectEToYe = () => false } = {}) {
      this.output = "";
      this.cursorPos = 0;
      this.initial = "";
      this.medial = "";
      this.final = "";
      this.eToYeAutocorrected = false;
      this.shouldAutocorrectEToYe = shouldAutocorrectEToYe;
      this.keyHistory = [];
    }

    clampCursor() {
      this.cursorPos = snapAtomicCursor(this.output, this.cursorPos);
    }

    hasBuffer() {
      return Boolean(this.initial || this.medial || this.final);
    }

    bufferText() {
      if (this.initial && this.medial) return composeSyllable(this.initial, this.medial, this.final);
      if (this.initial) return L_TO_COMPAT[this.initial] || this.initial;
      if (this.medial) return V_TO_COMPAT[this.medial] || this.medial;
      if (this.final) return T_TO_COMPAT[this.final] || this.final;
      return "";
    }

    text() {
      this.clampCursor();
      return `${this.output.slice(0, this.cursorPos)}${this.bufferText()}${this.output.slice(this.cursorPos)}`;
    }

    displayCursorPos() {
      this.clampCursor();
      return this.cursorPos + this.bufferText().length;
    }

    snapshot() {
      return [this.output, this.cursorPos, this.initial, this.medial, this.final, this.eToYeAutocorrected];
    }

    restore(snapshot) {
      [this.output, this.cursorPos, this.initial, this.medial, this.final, this.eToYeAutocorrected] = snapshot;
      this.clampCursor();
    }

    setText(text, cursor = text.length) {
      this.output = normalizeApostrophes(text);
      this.cursorPos = Math.max(0, Math.min(cursor, this.output.length));
      this.initial = "";
      this.medial = "";
      this.final = "";
      this.eToYeAutocorrected = false;
      this.keyHistory = [];
    }

    commit() {
      if (!this.hasBuffer()) return;
      const text = this.bufferText();
      this.output = `${this.output.slice(0, this.cursorPos)}${text}${this.output.slice(this.cursorPos)}`;
      this.cursorPos += text.length;
      this.initial = "";
      this.medial = "";
      this.final = "";
      this.eToYeAutocorrected = false;
    }

    insertLiteral(text) {
      const normalized = normalizeApostrophes(text);
      this.commit();
      this.output = `${this.output.slice(0, this.cursorPos)}${normalized}${this.output.slice(this.cursorPos)}`;
      this.cursorPos += normalized.length;
      this.keyHistory = [];
    }

    moveLeft() {
      this.commit();
      this.clampCursor();
      if (this.cursorPos > 0) {
        this.cursorPos -= 1;
        const bounds = atomicHangulClusterBoundsAt(this.output, this.cursorPos);
        if (bounds) this.cursorPos = bounds[0];
      }
      this.keyHistory = [];
    }

    moveRight() {
      this.commit();
      this.clampCursor();
      if (this.cursorPos < this.output.length) {
        const end = atomicHangulClusterEndAt(this.output, this.cursorPos);
        const bounds = atomicHangulClusterBoundsAt(this.output, this.cursorPos);
        this.cursorPos = end ?? bounds?.[1] ?? this.cursorPos + 1;
      }
      this.keyHistory = [];
    }

    addInitial(initial, sourceCompat = "") {
      if (!this.hasBuffer()) {
        this.initial = initial;
        this.eToYeAutocorrected = false;
        return;
      }
      if (!this.initial && this.medial === "ᅳ" && !this.final && sourceCompat === "ㅇ") {
        this.medial = "";
        this.initial = "ᅙ";
        this.eToYeAutocorrected = false;
        return;
      }
      if (this.initial && !this.medial) {
        const previousCompat = L_TO_COMPAT[this.initial] || "";
        if (previousCompat in COMPAT_TO_T && sourceCompat in COMPAT_TO_T) {
          const candidate = T_COMBINE[`${COMPAT_TO_T[previousCompat]}${COMPAT_TO_T[sourceCompat]}`];
          if (candidate) {
            this.initial = "";
            this.final = candidate;
            this.eToYeAutocorrected = false;
            return;
          }
        }
        this.commit();
        this.initial = initial;
        this.eToYeAutocorrected = false;
        return;
      }
      if (
        this.initial && this.medial && !this.final && sourceCompat && canBeFinal(sourceCompat) &&
        (sourceCompat !== "ㅈ" || this.medial in FINAL_J_SHORTCUT_MEDIALS)
      ) {
        this.final = COMPAT_TO_T[sourceCompat];
        const corrected = composeSyllable(this.initial, "ᅨ", this.final);
        if (
          this.medial === "ᅦ" &&
          ["ᆨ", "ᆼ"].includes(this.final) &&
          this.shouldAutocorrectEToYe(corrected)
        ) {
          this.medial = "ᅨ";
          this.eToYeAutocorrected = true;
        } else {
          this.eToYeAutocorrected = false;
        }
        return;
      }
      if (this.initial && this.medial && this.final && sourceCompat && canBeFinal(sourceCompat)) {
        const candidate = T_COMBINE[`${this.final}${COMPAT_TO_T[sourceCompat]}`];
        if (candidate) {
          this.final = candidate;
          this.eToYeAutocorrected = false;
          return;
        }
      }
      this.commit();
      this.initial = initial;
      this.eToYeAutocorrected = false;
    }

    addVowel(medial, allowNativeSpecial = false) {
      if (!this.hasBuffer()) {
        this.medial = medial;
        this.eToYeAutocorrected = false;
        return;
      }
      if (!this.initial && this.medial && !this.final) {
        const pair = `${this.medial}${medial}`;
        const candidate = V_COMBINE[pair] || (allowNativeSpecial ? NATIVE_V_COMBINE[pair] : "");
        if (candidate) {
          if (SPECIAL_MEDIALS.has(candidate)) {
            this.medial = "";
            const onset = NATIVE_SPECIAL_MEDIAL_ONSET[candidate] || HANGUL_CHOSEONG_FILLER;
            this.insertLiteral(`${onset}${candidate}`);
          } else {
            this.medial = candidate;
          }
          this.eToYeAutocorrected = false;
          return;
        }
        this.commit();
        this.medial = medial;
        this.eToYeAutocorrected = false;
        return;
      }
      if (this.initial && !this.medial) {
        this.medial = medial;
        this.eToYeAutocorrected = false;
        return;
      }
      if (this.initial && this.medial && !this.final) {
        const pair = `${this.medial}${medial}`;
        const candidate = V_COMBINE[pair] || (allowNativeSpecial ? NATIVE_V_COMBINE[pair] : "");
        if (candidate) {
          this.medial = candidate;
          this.eToYeAutocorrected = false;
          return;
        }
        this.commit();
        if (SPECIAL_MEDIALS.has(medial)) {
          this.insertLiteral(`${HANGUL_CHOSEONG_FILLER}${medial}`);
        } else {
          this.medial = medial;
        }
        this.eToYeAutocorrected = false;
        return;
      }
      if (this.initial && this.medial && this.final) {
        if (this.eToYeAutocorrected && this.medial === "ᅨ" && ["ᆨ", "ᆼ"].includes(this.final)) {
          this.medial = "ᅦ";
          this.eToYeAutocorrected = false;
        }
        if (this.final in T_SPLIT) {
          const [keepFinal, moveFinal] = T_SPLIT[this.final];
          this.final = keepFinal;
          this.commit();
          this.initial = T_TO_L[moveFinal] || "";
          this.medial = medial;
          this.eToYeAutocorrected = false;
        } else {
          const moveInitial = T_TO_L[this.final] || "";
          if (!moveInitial) {
            this.commit();
            this.initial = "ᄋ";
            this.medial = medial;
          } else {
            this.final = "";
            this.commit();
            this.initial = moveInitial;
            this.medial = medial;
          }
          this.eToYeAutocorrected = false;
        }
        return;
      }
      this.commit();
      this.initial = "ᄋ";
      this.medial = medial;
      this.eToYeAutocorrected = false;
    }

    backspace() {
      if (this.final) {
        if (this.eToYeAutocorrected) {
          this.final = "";
          this.medial = "ᅦ";
          this.eToYeAutocorrected = false;
          return;
        }
        if (this.final in T_SPLIT) this.final = T_SPLIT[this.final][0];
        else this.final = "";
        this.eToYeAutocorrected = false;
        return;
      }
      if (this.medial) {
        const reverse = Object.fromEntries(Object.entries(V_COMBINE).map(([key, value]) => [value, key[0]]));
        if (this.medial in reverse) this.medial = reverse[this.medial];
        else if (["ᅷ", "ᆤ"].includes(this.medial)) this.medial = "";
        else if (this.medial in SPECIAL_MEDIAL_BACKSPACE_BASE) {
          this.medial = SPECIAL_MEDIAL_BACKSPACE_BASE[this.medial];
        } else this.medial = "";
        this.eToYeAutocorrected = false;
        return;
      }
      if (this.initial) {
        this.initial = "";
        this.eToYeAutocorrected = false;
        return;
      }
      this.clampCursor();
      if (this.cursorPos > 0) {
        const cluster = atomicHangulClusterBoundsEndingAt(this.output, this.cursorPos);
        if (cluster) {
          const [start, end] = cluster;
          this.output = `${this.output.slice(0, start)}${this.output.slice(end)}`;
          this.cursorPos = start;
          this.keyHistory = [];
          return;
        }

        if (
          this.cursorPos >= 2 &&
          this.output[this.cursorPos - 2] === HANGUL_CHOSEONG_FILLER &&
          ["ᅷ", "ᆤ"].includes(this.output[this.cursorPos - 1])
        ) {
          this.output = `${this.output.slice(0, this.cursorPos - 2)}${this.output.slice(this.cursorPos)}`;
          this.cursorPos -= 2;
          this.keyHistory = [];
          return;
        }

        if (
          this.cursorPos >= 2 &&
          this.output[this.cursorPos - 2] === HANGUL_CHOSEONG_FILLER &&
          this.output[this.cursorPos - 1] === "ힻ"
        ) {
          this.output = `${this.output.slice(0, this.cursorPos - 2)}${this.output.slice(this.cursorPos)}`;
          this.cursorPos -= 2;
          this.medial = "ᅳ";
          this.keyHistory = [];
          return;
        }

        if (
          this.cursorPos >= 2 &&
          ["ᅷ", "ᆤ"].includes(this.output[this.cursorPos - 1]) &&
          isInitialJamo(this.output[this.cursorPos - 2])
        ) {
          const initial = this.output[this.cursorPos - 2];
          this.output = `${this.output.slice(0, this.cursorPos - 2)}${this.output.slice(this.cursorPos)}`;
          this.cursorPos -= 2;
          this.initial = initial;
          this.keyHistory = [];
          return;
        }

        if (
          this.cursorPos >= 2 &&
          this.output[this.cursorPos - 1] in SPECIAL_MEDIAL_BACKSPACE_BASE &&
          isInitialJamo(this.output[this.cursorPos - 2])
        ) {
          const initial = this.output[this.cursorPos - 2];
          const special = this.output[this.cursorPos - 1];
          this.output = `${this.output.slice(0, this.cursorPos - 2)}${this.output.slice(this.cursorPos)}`;
          this.cursorPos -= 2;
          this.initial = initial;
          this.medial = SPECIAL_MEDIAL_BACKSPACE_BASE[special];
          this.keyHistory = [];
          return;
        }

        this.output = `${this.output.slice(0, this.cursorPos - 1)}${this.output.slice(this.cursorPos)}`;
        this.cursorPos -= 1;
      }
      this.keyHistory = [];
    }

    addTone(digit) {
      const mark = TONE_MARKS[digit];
      if (!mark) return;
      this.commit();
      const before = this.output[this.cursorPos - 1];
      if (isHangulishForTone(before)) {
        this.output = `${this.output.slice(0, this.cursorPos)}${mark}${this.output.slice(this.cursorPos)}`;
        this.cursorPos += mark.length;
      } else {
        this.insertLiteral(digit);
      }
      this.keyHistory = [];
    }

    handleCompat(compat, allowNativeSpecial = false) {
      if (compat in COMPAT_TO_V) this.addVowel(COMPAT_TO_V[compat], allowNativeSpecial);
      else if (compat in COMPAT_TO_L) this.addInitial(COMPAT_TO_L[compat], compat);
      else this.insertLiteral(compat);
    }

    startMappedCluster(mapped) {
      this.commit();
      if (mapped.length >= 2 && isInitialJamo(mapped[0]) && isVowelJamo(mapped[1])) {
        this.initial = mapped[0];
        this.medial = mapped[1];
        this.final = mapped[2] in T_INDEX ? mapped[2] : "";
        if (mapped.length > 3) {
          this.commit();
          this.insertLiteral(mapped.slice(3));
        }
      } else {
        this.insertLiteral(mapped);
      }
    }

    processChar(char) {
      const normalized = normalizeKeyboardChar(normalizeApostrophes(char));
      if (normalized in TONE_INPUT) {
        this.addTone(TONE_INPUT[normalized]);
        return;
      }
      if ("12345".includes(normalized)) {
        this.addTone(normalized);
        return;
      }
      if (!(normalized in KEY_TO_JAMO)) {
        this.insertLiteral(normalized);
        return;
      }

      const before = this.snapshot();
      this.handleCompat(KEY_TO_JAMO[normalized]);
      this.keyHistory.push([normalized, before]);
      if (this.keyHistory.length > MAX_SEQUENCE_LENGTH) {
        this.keyHistory = this.keyHistory.slice(-MAX_SEQUENCE_LENGTH);
      }
      const rawTail = this.keyHistory.map(([key]) => key).join("");
      const match = Object.entries(HOKKIEN_SEQUENCE_MAP)
        .sort((a, b) => b[0].length - a[0].length)
        .find(([sequence]) => rawTail.endsWith(sequence));
      if (match) {
        const startIndex = this.keyHistory.length - match[0].length;
        this.restore(this.keyHistory[startIndex][1]);
        this.startMappedCluster(match[1]);
        this.keyHistory = [];
      }
    }

    processCompat(char) {
      if (char in COMPAT_TO_L || char in COMPAT_TO_V) this.handleCompat(char);
      else this.insertLiteral(char);
      this.keyHistory = [];
    }

    processNativeCompat(char) {
      if (char in COMPAT_TO_L || char in COMPAT_TO_V) this.handleCompat(char, true);
      else this.insertLiteral(char);
      this.keyHistory = [];
    }
  }

  function normalizeNativeCandidateInput(value) {
    const chars = [...String(value ?? "")];
    const composer = new Composer();
    for (let index = 0; index < chars.length; index += 1) {
      const char = chars[index];
      if (char === HANGUL_CHOSEONG_FILLER && chars[index + 1] in NATIVE_SPECIAL_VOWEL_INPUT) {
        composer.insertLiteral(`${char}${chars[index + 1]}`);
        index += 1;
        continue;
      }
      for (const unit of nativeKoreanInputUnits(char)) {
        if (unit.compose) composer.processNativeCompat(unit.text);
        else composer.insertLiteral(unit.text);
      }
    }
    composer.commit();
    let output = "";
    for (const char of composer.text()) {
      const code = char.codePointAt(0);
      const offset = code - 0xac00;
      const final = offset >= 0 && offset < 11172 ? T_TABLE[offset % 28] : "";
      if (final === "ᆽ") {
        const initial = L_TABLE[Math.floor(offset / 588)];
        const medial = V_TABLE[Math.floor((offset % 588) / 28)];
        const specialMedial = FINAL_J_SHORTCUT_MEDIALS[medial];
        if (specialMedial) {
          output += `${initial}${specialMedial}`;
          continue;
        }
      }
      output += char;
    }
    return output;
  }

  return {
    Composer,
    containsNativeKoreanInput,
    composeNativeVowelInputs,
    keyboardGuideOutput,
    nativeKoreanInputUnits,
    nativeStandaloneVowelAt,
    nativeStandaloneVowelInputs,
    normalizeNativeCandidateInput,
    normalizeDisallowedFinalInputText,
    normalizeAtomicSelection,
    normalizeReadingBase,
    normalizeReadingToneKey,
  };
})();

window.TangliengimHangulIme = TangliengimHangulIme;
