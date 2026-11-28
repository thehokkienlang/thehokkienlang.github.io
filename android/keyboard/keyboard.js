// The Android keyboard's page. It runs inside the keyboard's WebView and reuses the web IME
// unchanged: the on-screen keys feed the same text-control IME the website uses, and the
// buffer it edits is sent to the focused app as composing text.
(() => {
  "use strict";
  // In a desktop browser (for layout work) there is no host; log instead.
  const host = window.TliHost || {
    setComposing: text => console.log("composing:", text),
    commit: text => console.log("commit:", JSON.stringify(text)),
    deleteBackward: () => console.log("delete"),
    enter: () => console.log("enter"),
    showKeyboardPicker: () => console.log("keyboard picker"),
  };
  const core = window.TangliengimImeCore;
  const hangul = window.TangliengimHangulIme;
  const buffer = document.querySelector("#buffer");
  const candidates = document.querySelector("#candidates");
  const keys = document.querySelector("#keys");

  // TLI writes the apostrophe as part of its spelling (食飽’쀄), so it has its own key at the end
  // of the home row, where ' sits on a physical QWERTY keyboard.
  const APOSTROPHE = "’";
  // The bottom row and the symbol pages follow Gboard's English layout.
  const BOTTOM = [",", "Emoji", "Space", ".", "Enter"];
  const LAYERS = {
    tli: [
      [..."qwertyuiop"],
      [..."asdfghjkl", APOSTROPHE],
      ["Shift", ..."zxcvbnm", "Backspace"],
      ["Symbols", ...BOTTOM],
    ],
    symbols: [
      [..."1234567890"],
      [..."@#$_&-+()/"],
      ["Symbols2", ..."*\"':;!?", "Backspace"],
      ["Letters", ...BOTTOM],
    ],
    symbols2: [
      [..."~`|•√π÷×§∆"],
      [..."£¢€¥^°={}\\"],
      ["Symbols", ..."%©®™✓[]", "Backspace"],
      ["Letters", "<", "Emoji", "Space", ">", "Enter"],
    ],
  };
  const CONTROL_LABELS = {
    Shift: "⇧", Backspace: "⌫", Enter: "⏎", Emoji: "☺", Symbols: "?123", Symbols2: "=\\<",
    Letters: "ㄱㄴㄷ", Space: "閩南語",
  };
  const EMOJI = [..."😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👻💀👽🤖💩😺😸😹😻😼😽🙀😿😾👍👎👌🤌🤏🤞🤟🤘🤙👈👉👆👇👋🤚🖐✋🖖👏🙌👐🤲🙏💪🫶💖💗💓💞💕💘💝💔🧡💛💚💙💜🖤🤍🤎💯💢💥💫💦💨🔥⭐🌟✨🎉🎊🎁🎂🍰🍜🍚🍵🍺🍻🥂☕🌸🌺🌻🌹🍀🌈☀🌙⛅🌧⚡❄🐶🐱🐭🐹🐰🦊🐻🐼🐯🦁🐮🐷🐸🐵🐔🐧🐦🦆🦉🐴🦄🐝🦋🐢🐍🐙🐠🐬🐳"];
  let layer = "tli";
  let shifted = false;
  let lastSent = "";

  // In candidates a tone sits above its Hangul in the lower form (ꞈ ˎ ˏ ˍ), as on the website.
  // A tone key shows its mark alone, with no Hangul to sit above, so it uses the upper form (ˆ ˋ ˊ ˉ).
  const UPPER_TONES = TangliengimEngine.UPPER_HANGUL_TONE_MARKS;
  const upperTone = mark => UPPER_TONES[mark] || mark;

  // Some Hanri are missing from most fonts, so the receiving app would show an empty box. Those
  // characters are written in Hangul instead: anything beyond the Basic Multilingual Plane
  // (CJK Extension B and later), and anything this phone's own fonts cannot draw.
  const HAN = /\p{Script=Han}/u;
  const fontSupport = new Map();
  const probe = document.createElement("canvas").getContext?.("2d", { willReadFrequently: true });
  function drawn(char) {
    probe.clearRect(0, 0, 32, 32);
    probe.fillText(char, 2, 2);
    return probe.getImageData(0, 0, 32, 32).data.join("");
  }
  let missingGlyph = null;
  if (probe) {
    probe.canvas.width = probe.canvas.height = 32;
    probe.font = "24px sans-serif"; // the system fonts only, not the keyboard's own web fonts
    probe.textBaseline = "top";
    missingGlyph = drawn("\u{10FFFD}");
  }
  function widelySupported(char) {
    if (!HAN.test(char)) return true;
    if (char.codePointAt(0) > 0xFFFF) return false;
    if (!probe) return true;
    if (!fontSupport.has(char)) fontSupport.set(char, drawn(char) !== missingGlyph);
    return fontSupport.get(char);
  }
  // 到𦤾 becomes 到달: each unsupported character is replaced by its own syllable. Returns the
  // pieces, each marked as Hanri or Hangul, or null when every character is widely supported.
  function writtenParts(entry) {
    const chars = [...entry.hanri];
    if (chars.every(widelySupported)) return null;
    const base = entry.readingBase || hangul.normalizeReadingBase(entry.reading || "");
    const units = [];
    for (let index = 0; index < base.length;) {
      const unit = core.readingUnitAt(base, index);
      if (!unit) break;
      units.push(unit.text);
      index = unit.end;
    }
    if (units.length !== chars.length) return base ? [{ text: base, hangul: true }] : null;
    return chars.map((char, index) => (widelySupported(char)
      ? { text: char, hangul: false }
      : { text: units[index], hangul: true }));
  }
  // A Hanri this phone may draw as an empty box keeps its candidate, and a second candidate
  // right after it offers the same word with those characters in Hangul (到𦤾, then 到달).
  // The user picks whichever reads correctly on their screen.
  function offerHangulForRareHanri() {
    [...candidates.querySelectorAll(".ime-candidate")].forEach((button, index) => {
      const candidate = controller.activeCandidates[index];
      if (!candidate || ["hangul_override", "hangul_plain"].includes(candidate.entry.kind)) return;
      const parts = writtenParts(candidate.entry);
      if (!parts) return;
      const written = parts.map(part => part.text).join("");
      const option = button.cloneNode(true);
      option.classList.remove("selected");
      option.classList.add("candidate-written");
      option.setAttribute("aria-selected", "false");
      option.dataset.start = candidate.start;
      option.dataset.hanri = candidate.entry.hanri;
      option.dataset.written = written;
      // The Hangul goes in the Hangul font, which joins old-style jamo such as ᄁᅷ into one
      // syllable; the Hanri font beside it would draw them as loose letters.
      option.querySelector(".candidate-hanri").replaceChildren(...parts.map(part => {
        if (!part.hangul) return part.text;
        const span = document.createElement("span");
        span.className = "written-hangul";
        span.textContent = part.text;
        return span;
      }));
      // The IME applies the candidate (its tones and learning); the click below swaps the text.
      option.addEventListener("click", () => controller.applyCandidate(candidate, true));
      button.after(option);
    });
  }

  const controller = core.createTextImeController({
    control: buffer,
    candidateContainer: candidates,
    enabled: () => true,
    onUpdate: sync,
    onCandidatesChanged: () => { offerHangulForRareHanri(); candidates.scrollLeft = 0; },
    enterBehavior: "none",
    candidateLimit: 24,
  });

  function sync() {
    const text = buffer.value;
    document.body.classList.toggle("composing", Boolean(text));
    if (text === lastSent) return;
    lastSent = text;
    host.setComposing(text);
  }

  // Hand the buffer to the app as finished text, followed by `suffix` in the same commit.
  function commitBuffer(replacement = null, suffix = "") {
    let text = buffer.value;
    if (!text) return false;
    if (replacement && text.startsWith(replacement.hanri, replacement.start)) {
      text = text.slice(0, replacement.start) + replacement.written +
        text.slice(replacement.start + replacement.hanri.length);
    }
    host.commit(text + suffix);
    lastSent = "";
    controller.clear();
    return true;
  }

  // The app moved on (new field, cursor moved away): drop the buffer without touching its text.
  function reset() {
    lastSent = "";
    if (buffer.value) controller.clear();
    setShift(false);
  }

  // Tones have no row of their own. Shift (or a hold) on ㅛ ㅕ ㅑ ㅐ types tones 1 2 4 5: none of
  // those keys has a shifted Hangul that TLI uses.
  const TONE_KEYS = { y: "1", u: "2", i: "4", o: "5" };
  const toneLabel = key => upperTone(hangul.keyboardGuideOutput(TONE_KEYS[key]));

  // Send key input to the IME. A tone after a syllable stays hidden in the text and only picks
  // the candidates, which show its mark (가ꞈ). With no syllable before it, the IME would type
  // the digit instead, so the mark itself is typed.
  function insertInput(input) {
    if (Object.values(TONE_KEYS).includes(input)) {
      const cursor = buffer.selectionStart ?? buffer.value.length;
      if (!controller.previousHangulUnit(buffer.value, cursor)) {
        commitBuffer();
        host.commit(hangul.keyboardGuideOutput(input));
        return;
      }
    }
    controller.insertText(input);
  }

  function inputFor(key) {
    if (!shifted) return key;
    return TONE_KEYS[key] || key.toUpperCase();
  }

  function setShift(next) {
    if (shifted === next) return;
    shifted = next;
    render();
  }

  function press(key) {
    switch (key) {
      case "Shift": setShift(!shifted); return;
      case "Symbols": layer = "symbols"; shifted = false; render(); return;
      case "Symbols2": layer = "symbols2"; render(); return;
      case "Emoji": layer = "emoji"; shifted = false; render(); return;
      case "Letters": layer = "tli"; render(); return;
      case "Backspace":
        if (buffer.value) controller.backspace(); else host.deleteBackward();
        return;
      case "Space":
        // One press finishes the composition and types the space, as on Gboard's Korean keyboard.
        if (!commitBuffer(null, " ")) host.commit(" ");
        return;
      case "Enter":
        if (!commitBuffer()) host.enter();
        return;
    }
    if (layer === "tli" && key === APOSTROPHE) {
      controller.insertText(APOSTROPHE);
      if (shifted) setShift(false);
      return;
    }
    if (layer !== "tli" || key === "," || key === ".") {
      commitBuffer();
      host.commit(key);
      return;
    }
    insertInput(inputFor(key));
    if (shifted) setShift(false);
  }

  function makeKey(key) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "key";
    button.dataset.key = key;
    if (key in CONTROL_LABELS) {
      button.classList.add("control", "key-" + key.toLowerCase());
      button.textContent = CONTROL_LABELS[key];
      if (key === "Shift") button.classList.toggle("active", shifted);
    } else if (layer === "tli" && /^[a-z]$/.test(key)) {
      const output = document.createElement("span");
      output.className = "key-output";
      output.textContent = upperTone(hangul.keyboardGuideOutput(inputFor(key)) || key);
      const input = document.createElement("span");
      input.className = "key-input";
      // The corner shows what Shift or a hold gives on a tone key, and the Latin letter elsewhere.
      input.textContent = TONE_KEYS[key] && !shifted ? toneLabel(key) : inputFor(key);
      if (TONE_KEYS[key]) {
        button.classList.toggle("tone", shifted);
        input.classList.add("key-hint-tone");
      }
      button.append(output);
      if (!(TONE_KEYS[key] && shifted)) button.append(input);
    } else {
      button.textContent = key;
    }
    return button;
  }

  function render() {
    cancelPending();
    keys.dataset.layer = layer;
    if (layer === "emoji") {
      const grid = document.createElement("div");
      grid.className = "emoji-grid";
      grid.append(...EMOJI.map(emoji => {
        const button = makeKey(emoji);
        button.classList.add("emoji");
        return button;
      }));
      const bottom = document.createElement("div");
      bottom.className = "row row-emoji-bottom";
      bottom.append(...["Letters", "Space", "Backspace", "Enter"].map(makeKey));
      keys.replaceChildren(grid, bottom);
      return;
    }
    keys.replaceChildren(...LAYERS[layer].map((row, index) => {
      const element = document.createElement("div");
      element.className = `row row-${layer}-${index}`;
      element.append(...row.map(makeKey));
      return element;
    }));
  }

  // Holding a key offers more characters, as on Gboard's English keyboard. A letter offers its
  // shifted Hangul (ㄱ gives ㄲ) and the digit or symbol Gboard puts on that key (q 1, a @, s #,
  // d $ ...); a key on the symbol pages offers Gboard's related symbols.
  const LETTER_SYMBOLS = {
    q: "1", w: "2", e: "3", r: "4", t: "5", y: "6", u: "7", i: "8", o: "9", p: "0",
    a: "@", s: "#", d: "$", f: "_", g: "&", h: "-", j: "+", k: "(", l: ")",
    z: "*", x: "\"", c: "'", v: ":", b: ";", n: "!", m: "?",
  };
  const SYMBOL_ALTERNATES = {
    "1": "¹½⅓¼⅛", "2": "²⅔", "3": "³¾⅜", "4": "⁴", "5": "⅝", "7": "⅞", "0": "ⁿ∅",
    "#": "№", "$": "¢£€¥₱", "-": "_–—·", "+": "±", "(": "<{[", ")": ">}]",
    "*": "†‡★", "\"": "„“”«»", "'": "‚‘’‹›", "!": "¡", "?": "¿‽",
    "•": "♪♥♠♦♣", "π": "Π", "§": "¶", "^": "←↑↓→", "°": "′″", "=": "≠≈∞",
    "%": "‰℅", "<": "≤«‹", ">": "≥»›",
    ".": "?!:;'\"-@",
  };
  function alternatesFor(key) {
    const text = chars => [...chars].map(char => ({ label: char, text: char }));
    if (layer === "tli" && /^[a-z]$/.test(key)) {
      const alternates = [];
      const upper = key.toUpperCase();
      const output = hangul.keyboardGuideOutput(upper);
      if (!shifted && TONE_KEYS[key]) {
        alternates.push({ label: toneLabel(key), input: TONE_KEYS[key] });
      } else if (!shifted && output && output !== hangul.keyboardGuideOutput(key)) {
        alternates.push({ label: output, input: upper });
      }
      return [...alternates, ...text(LETTER_SYMBOLS[key] || "")];
    }
    if (layer === "tli" && key !== ".") return [];
    return text(SYMBOL_ALTERNATES[key] || "");
  }

  // Character keys type on release, so a hold can be told from a tap. Controls act on touch-down.
  const HOLD_MS = 320;
  let repeatTimer = null;
  let spaceHeld = false;
  let pending = null; // { button, key, timer, popup, choice }

  function closePopup() {
    pending?.popup?.remove();
    if (pending) pending.popup = null;
  }

  function openPopup() {
    const alternates = alternatesFor(pending.key);
    if (!alternates.length) return;
    const popup = document.createElement("div");
    popup.className = "key-popup";
    popup.append(...alternates.map((alternate, index) => {
      const option = document.createElement("span");
      option.className = "key-popup-option";
      option.textContent = alternate.label;
      option.dataset.index = index;
      return option;
    }));
    document.body.append(popup);
    const key = pending.button.getBoundingClientRect();
    const box = popup.getBoundingClientRect();
    const left = Math.min(Math.max(4, key.left + key.width / 2 - box.width / 2), innerWidth - box.width - 4);
    popup.style.left = `${left}px`;
    popup.style.top = `${Math.max(2, key.top - box.height - 6)}px`;
    pending.popup = popup;
    pending.alternates = alternates;
    choose(0);
  }

  function choose(index) {
    pending.choice = index;
    pending.popup.querySelectorAll(".key-popup-option").forEach((option, position) => {
      option.classList.toggle("selected", position === index);
    });
  }

  function typeAlternate(alternate) {
    if (alternate.input) {
      insertInput(alternate.input);
    } else {
      commitBuffer();
      host.commit(alternate.text);
    }
  }

  // Type the key that is waiting: its chosen alternate after a hold, itself after a tap.
  function finishPending() {
    if (!pending) return;
    const { key, timer, popup, alternates, choice, button } = pending;
    clearTimeout(timer);
    popup?.remove();
    button.classList.remove("pressed");
    pending = null;
    if (popup) typeAlternate(alternates[choice]);
    else press(key);
  }

  function cancelPending() {
    if (!pending) return;
    clearTimeout(pending.timer);
    pending.popup?.remove();
    pending.button.classList.remove("pressed");
    pending = null;
  }

  function stopRepeat() {
    clearTimeout(repeatTimer);
    repeatTimer = null;
    keys.querySelectorAll(".pressed").forEach(button => {
      if (button !== pending?.button) button.classList.remove("pressed");
    });
  }

  keys.addEventListener("pointerdown", event => {
    const button = event.target.closest(".key");
    if (!button) return;
    event.preventDefault();
    // The web IME closes its candidates on any outside tap; a key press is not one.
    event.stopPropagation();
    const key = button.dataset.key;
    // The emoji grid scrolls, so its keys act on a tap (click), not on touch-down.
    if (button.classList.contains("emoji")) return;
    // A second finger landing means the first key is done (fast two-thumb typing).
    finishPending();
    button.classList.add("pressed");
    if (key === "Space") {
      // A tap types a space; holding the space bar opens the system keyboard picker.
      spaceHeld = false;
      repeatTimer = setTimeout(() => { spaceHeld = true; commitBuffer(); host.showKeyboardPicker(); }, 500);
      return;
    }
    if (key in CONTROL_LABELS) {
      press(key);
      if (key === "Backspace") {
        const repeat = () => { press("Backspace"); repeatTimer = setTimeout(repeat, 60); };
        repeatTimer = setTimeout(repeat, 400);
      }
      return;
    }
    // Keep the rest of the gesture on this key, wherever the finger slides.
    try { button.setPointerCapture(event.pointerId); } catch { /* the pointer is already gone */ }
    pending = { button, key, popup: null, choice: null, timer: setTimeout(openPopup, HOLD_MS) };
  });
  // As on Gboard, sliding sideways picks an alternate: only the finger's horizontal position
  // counts, so it need not reach the popup's row. Past either end, the end option stays chosen.
  keys.addEventListener("pointermove", event => {
    if (!pending?.popup) return;
    const options = [...pending.popup.querySelectorAll(".key-popup-option")];
    let index = options.findIndex(option => event.clientX < option.getBoundingClientRect().right);
    if (index < 0) index = options.length - 1;
    if (index !== pending.choice) choose(index);
  });
  keys.addEventListener("pointerup", event => {
    const button = event.target.closest(".key");
    if (pending && button === pending.button) finishPending();
    else if (button?.dataset.key === "Space" && button.classList.contains("pressed") && !spaceHeld) press("Space");
  });
  keys.addEventListener("pointercancel", cancelPending);
  for (const type of ["pointerup", "pointercancel", "pointerleave"]) keys.addEventListener(type, stopRepeat);
  keys.addEventListener("click", event => {
    const button = event.target.closest(".key.emoji");
    if (button) press(button.dataset.key);
  });
  document.addEventListener("contextmenu", event => event.preventDefault());

  // The IME applies the tapped candidate to the buffer first; then the buffer is finished.
  candidates.addEventListener("click", event => {
    const button = event.target.closest(".ime-candidate");
    if (!button) return;
    const replacement = button.dataset.written
      ? { start: Number(button.dataset.start), hanri: button.dataset.hanri, written: button.dataset.written }
      : null;
    queueMicrotask(() => commitBuffer(replacement));
  });

  render();
  fetch("/public/data/hokkien-hanri-dict.json")
    .then(response => response.json())
    .then(data => {
      const index = core.createDictionaryIndex(data.entries || []);
      controller.setEntries(index.entries, index);
    })
    .catch(() => document.body.classList.add("no-dictionary"));

  // Asked for from the app's setup screen: forget which candidates this keyboard has learned.
  function resetLearned() {
    controller.preferences.reset();
    return true;
  }

  window.TliKeyboard = { reset, commitBuffer, resetLearned };
})();
