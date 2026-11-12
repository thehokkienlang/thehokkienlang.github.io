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
    switchKeyboard: () => console.log("switch keyboard"),
  };
  const core = window.TangliengimImeCore;
  const hangul = window.TangliengimHangulIme;
  const buffer = document.querySelector("#buffer");
  const candidates = document.querySelector("#candidates");
  const keys = document.querySelector("#keys");

  const LAYERS = {
    tli: [
      ["1", "2", "4", "5", "’"],
      [..."qwertyuiop"],
      [..."asdfghjkl"],
      ["Shift", ..."zxcvbnm", "Backspace"],
      ["Symbols", "Globe", "Space", "Enter"],
    ],
    symbols: [
      [..."1234567890"],
      ["，", "。", "、", "？", "！", "：", "；", "「", "」"],
      [".", ",", "?", "!", "'", "\"", "-", "(", ")"],
      ["@", "/", "~", "…", "·", "《", "》", "Backspace"],
      ["Letters", "Globe", "Space", "Enter"],
    ],
  };
  const CONTROL_LABELS = { Shift: "⇧", Backspace: "⌫", Enter: "⏎", Globe: "🌐", Symbols: "?123", Letters: "한", Space: "" };
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
  // 到𦤾 becomes 到달: each unsupported character is replaced by its own syllable.
  function writtenForm(entry) {
    const chars = [...entry.hanri];
    if (chars.every(widelySupported)) return entry.hanri;
    const base = entry.readingBase || hangul.normalizeReadingBase(entry.reading || "");
    const units = [];
    for (let index = 0; index < base.length;) {
      const unit = core.readingUnitAt(base, index);
      if (!unit) break;
      units.push(unit.text);
      index = unit.end;
    }
    if (units.length !== chars.length) return base || entry.hanri;
    return chars.map((char, index) => (widelySupported(char) ? char : units[index])).join("");
  }
  function defaultRareHanriToHangul() {
    [...candidates.querySelectorAll(".ime-candidate")].forEach((button, index) => {
      const candidate = controller.activeCandidates[index];
      if (!candidate || ["hangul_override", "hangul_plain"].includes(candidate.entry.kind)) return;
      const written = writtenForm(candidate.entry);
      if (written === candidate.entry.hanri) return;
      button.dataset.start = candidate.start;
      button.dataset.hanri = candidate.entry.hanri;
      button.dataset.written = written;
      button.querySelector(".candidate-hanri").textContent = written;
      // Entirely Hangul now: the plain Hangul candidate already offers it.
      if (![...written].some(char => HAN.test(char))) button.hidden = true;
    });
  }

  const controller = core.createTextImeController({
    control: buffer,
    candidateContainer: candidates,
    enabled: () => true,
    onUpdate: sync,
    onCandidatesChanged: () => { defaultRareHanriToHangul(); candidates.scrollLeft = 0; },
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

  // Hand the buffer to the app as finished text.
  function commitBuffer(replacement = null) {
    let text = buffer.value;
    if (!text) return false;
    if (replacement && text.startsWith(replacement.hanri, replacement.start)) {
      text = text.slice(0, replacement.start) + replacement.written +
        text.slice(replacement.start + replacement.hanri.length);
    }
    host.commit(text);
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

  function inputFor(key) {
    return shifted ? key.toUpperCase() : key;
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
      case "Letters": layer = "tli"; render(); return;
      case "Globe": commitBuffer(); host.switchKeyboard(); return;
      case "Backspace":
        if (buffer.value) controller.backspace(); else host.deleteBackward();
        return;
      case "Space":
        // Like other CJK keyboards: the first space finishes the composition, the next types a space.
        if (!commitBuffer()) host.commit(" ");
        return;
      case "Enter":
        if (!commitBuffer()) host.enter();
        return;
    }
    if (layer === "symbols") {
      commitBuffer();
      host.commit(key);
      return;
    }
    controller.insertText(inputFor(key));
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
    } else if (layer === "tli") {
      const output = document.createElement("span");
      output.className = "key-output";
      output.textContent = upperTone(hangul.keyboardGuideOutput(inputFor(key)) || key);
      const input = document.createElement("span");
      input.className = "key-input";
      input.textContent = inputFor(key);
      if (/^[0-9]$/.test(key)) button.classList.add("tone");
      button.append(output, input);
    } else {
      button.textContent = key;
    }
    return button;
  }

  function render() {
    keys.replaceChildren(...LAYERS[layer].map((row, index) => {
      const element = document.createElement("div");
      element.className = `row row-${layer}-${index}`;
      element.append(...row.map(makeKey));
      return element;
    }));
  }

  // Act on touch-down, and repeat Backspace while it is held.
  let repeatTimer = null;
  function stopRepeat() {
    clearTimeout(repeatTimer);
    repeatTimer = null;
    keys.querySelectorAll(".pressed").forEach(button => button.classList.remove("pressed"));
  }
  keys.addEventListener("pointerdown", event => {
    const button = event.target.closest(".key");
    if (!button) return;
    event.preventDefault();
    // The web IME closes its candidates on any outside tap; a key press is not one.
    event.stopPropagation();
    const key = button.dataset.key;
    button.classList.add("pressed");
    press(key);
    if (key === "Backspace") {
      const repeat = () => { press("Backspace"); repeatTimer = setTimeout(repeat, 60); };
      repeatTimer = setTimeout(repeat, 400);
    }
  });
  for (const type of ["pointerup", "pointercancel", "pointerleave"]) keys.addEventListener(type, stopRepeat);
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

  window.TliKeyboard = { reset, commitBuffer };
})();
