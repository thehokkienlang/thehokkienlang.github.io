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

  // The bottom row and the symbol pages follow Gboard's English layout.
  const BOTTOM = [",", "Emoji", "Space", ".", "Enter"];
  const LAYERS = {
    tli: [
      ["1", "2", "4", "5", "’"],
      [..."qwertyuiop"],
      [..."asdfghjkl"],
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
      case "Symbols2": layer = "symbols2"; render(); return;
      case "Emoji": layer = "emoji"; shifted = false; render(); return;
      case "Letters": layer = "tli"; render(); return;
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
    if (layer !== "tli" || key === "," || key === ".") {
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
    } else if (layer === "tli" && key !== "," && key !== ".") {
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

  // Holding a key offers more characters, as on Gboard: a letter offers its shifted form
  // (ㄱ gives ㄲ) and the period offers other punctuation.
  const PERIOD_ALTERNATES = [..."?!:;'\"-@"];
  function alternatesFor(key) {
    if (layer === "tli" && /^[a-z]$/.test(key) && !shifted) {
      const upper = key.toUpperCase();
      const output = hangul.keyboardGuideOutput(upper);
      if (output && output !== hangul.keyboardGuideOutput(key)) return [{ label: output, input: upper }];
    }
    if (key === ".") return PERIOD_ALTERNATES.map(char => ({ label: char, text: char }));
    return [];
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
      controller.insertText(alternate.input);
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
      // As on Gboard: a tap types, holding the space bar switches keyboards.
      spaceHeld = false;
      repeatTimer = setTimeout(() => { spaceHeld = true; commitBuffer(); host.switchKeyboard(); }, 500);
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
    pending = { button, key, popup: null, choice: null, timer: setTimeout(openPopup, HOLD_MS) };
  });
  keys.addEventListener("pointermove", event => {
    if (!pending?.popup) return;
    const option = document.elementFromPoint(event.clientX, event.clientY)?.closest?.(".key-popup-option");
    if (option) choose(Number(option.dataset.index));
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

  window.TliKeyboard = { reset, commitBuffer };
})();
