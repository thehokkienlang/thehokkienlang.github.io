const DATA_URL = "/public/data/hokkien-hanri-dict.json";

const imeText = document.querySelector("#imeText");
const clearButton = document.querySelector("#clearButton");
const copyButton = document.querySelector("#copyButton");
const audioButton = document.querySelector("#audioButton");
const taipeiButton = document.querySelector("#taipeiButton");
const singaporeButton = document.querySelector("#singaporeButton");
const candidateBar = document.querySelector("#candidateBar");
const lomariPreview = document.querySelector("#lomariPreview");
const statusLine = document.querySelector("#statusLine");
const toast = document.querySelector("#toast");
const textWrap = document.querySelector(".text-wrap");
const keyboardGuideButton = document.querySelector("#keyboardGuideButton");
const keyboardGuide = document.querySelector("#keyboardGuide");
const keyboardLayout = document.querySelector("#keyboardLayout");
const pad = document.querySelector(".pad");

const imeCore = window.TangliengimImeCore;
const phoneticCore = window.TangliengimPhoneticOutput;
const webAudio = window.TangliengimWebAudio;
let dictionaryIndex = imeCore.createDictionaryIndex([]);
const candidatePopup = imeCore.createCandidatePopupPositioner({
  control: imeText,
  container: candidateBar,
  boundary: textWrap,
  placement: "caret",
});
const imeController = imeCore.createTextImeController({
  control: imeText,
  candidateContainer: candidateBar,
  enabled: () => true,
  onUpdate: updateLomariPreview,
  onCandidatesChanged: candidatePopup.schedule,
  enterBehavior: "newline",
});

const state = {
  entries: [],
  unitRoman: new Map(),
  rawHangulAudio: new Map(),
  jamoLomari: new Map(),
  jamoAudio: new Map(),
  sandhiMode: "taipei",
};
const lomariRenderer = phoneticCore.createRenderer({
  imeCore,
  findHanriEntry,
  findHangulOverride,
  findHangulOverrideAt,
  findUnitRoman: (unit) => state.unitRoman.get(unit) || "",
  findJamoLomari: (unit) => state.jamoLomari.get(unit) || "",
});
const audioPlanner = phoneticCore.createAudioPlanner({
  imeCore,
  getSandhiMode: () => state.sandhiMode,
  findHanriEntry,
  findReadingEntry,
  findHangulOverrideAt,
  findJamoAudio: (unit) => state.jamoAudio.get(unit),
  findRawHangulAudio: (key) => state.rawHangulAudio.get(key),
  normalizeReadingToneKey: TangliengimHangulIme.normalizeReadingToneKey,
});
const audioPlayer = webAudio.createPlayer();
const guideButtons = new Map();
let guideShifted = false;

const GUIDE_ROWS = [
  ["1", "2", "4", "5", "Backspace"],
  [..."qwertyuiop"],
  [..."asdfghjkl"],
  ["Shift", ..."zxcvbnm", "’"],
  ["Space"],
];

const GUIDE_CONTROL_LABELS = Object.freeze({
  Shift: "⇧",
  Backspace: "⌫",
});

function guideInputForKey(key) {
  if (key === "Space") return " ";
  if (key === "’") return "’";
  if (key.length === 1 && /[a-z]/i.test(key)) {
    return guideShifted ? key.toUpperCase() : key.toLowerCase();
  }
  return key;
}

function guideOutputForKey(key) {
  if (["Shift", "Space", "’", "Backspace"].includes(key)) return "";
  return TangliengimHangulIme.keyboardGuideOutput(guideInputForKey(key));
}

function refreshGuideKey(key) {
  const button = guideButtons.get(key);
  if (!button) return;
  button.classList.toggle("modifier-active", key === "Shift" && guideShifted);
  const input = button.querySelector?.(".key-input");
  const output = button.querySelector?.(".key-output");
  if (input && key.length === 1 && /[a-z]/i.test(key)) {
    input.textContent = guideInputForKey(key);
  }
  if (output) output.textContent = guideOutputForKey(key);
}

function refreshGuideShiftState() {
  for (const row of GUIDE_ROWS) {
    for (const key of row) refreshGuideKey(key);
  }
}

function setGuidePressed(key, pressed) {
  guideButtons.get(key)?.classList.toggle("pressed", pressed);
}

function activateGuideKey(key) {
  if (key === "Shift") {
    guideShifted = !guideShifted;
    refreshGuideShiftState();
    return;
  }
  if (key === "Backspace") {
    imeController.backspace();
  } else {
    imeController.insertText(guideInputForKey(key));
  }
  if (guideShifted) {
    guideShifted = false;
    refreshGuideShiftState();
  }
}

function makeGuideKey(key) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "keyboard-key";
  button.setAttribute("data-key", key);
  if ("1245".includes(key)) button.classList.add("tone-key");
  if (["Shift", "Space", "Backspace"].includes(key)) {
    button.classList.add("control-key", `key-${key.toLowerCase()}`);
    button.textContent = GUIDE_CONTROL_LABELS[key] || key;
    button.setAttribute("aria-label", key);
    button.title = key;
  } else if (key === "’") {
    button.classList.add("control-key", "key-apostrophe");
    button.textContent = key;
    button.setAttribute("aria-label", "Apostrophe");
    button.title = "Apostrophe";
  } else {
    const input = document.createElement("span");
    input.className = "key-input";
    input.textContent = key;
    const output = document.createElement("span");
    output.className = "key-output";
    output.textContent = guideOutputForKey(key);
    button.append(input, output);
  }
  button.addEventListener("mousedown", (event) => event.preventDefault());
  button.addEventListener("pointerdown", () => setGuidePressed(key, true));
  button.addEventListener("pointerleave", () => setGuidePressed(key, false));
  button.addEventListener("pointerup", () => setGuidePressed(key, false));
  button.addEventListener("click", () => activateGuideKey(key));
  guideButtons.set(key, button);
  return button;
}

function renderKeyboardGuide() {
  keyboardLayout.replaceChildren();
  for (const keys of GUIDE_ROWS) {
    const row = document.createElement("div");
    row.className = "keyboard-row";
    if (keys.includes("Backspace")) row.classList.add("keyboard-row-top-controls");
    if (keys.includes("Shift")) row.classList.add("keyboard-row-bottom");
    for (const key of keys) row.append(makeGuideKey(key));
    keyboardLayout.append(row);
  }
}

function physicalGuideKey(event) {
  if (event.key === "Shift") return "Shift";
  if (event.key === "Backspace") return "Backspace";
  if (event.key === " " || event.code === "Space") return "Space";
  if (["'", "’"].includes(event.key)) return "’";
  const key = String(event.key || "").toLowerCase();
  return guideButtons.has(key) ? key : null;
}

function copyText(text) {
  if (navigator.clipboard?.writeText) {
    return navigator.clipboard.writeText(text);
  }

  const scratch = document.createElement("textarea");
  scratch.value = text;
  scratch.setAttribute("readonly", "");
  scratch.style.position = "fixed";
  scratch.style.opacity = "0";
  document.body.append(scratch);
  scratch.select();
  document.execCommand("copy");
  scratch.remove();
  return Promise.resolve();
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 1500);
}

function setEntries(entries) {
  dictionaryIndex = imeCore.createDictionaryIndex(entries);
  state.entries = dictionaryIndex.entries;
}

function findHanriEntry(text, index) {
  return imeController.findRememberedHanriEntry(text, index) || dictionaryIndex.findHanriEntry(
    text,
    index,
    imeController.nextRememberedHanriStart(text, index)
  );
}

function findReadingEntry(reading) {
  return dictionaryIndex.findReadingEntry(reading);
}

function findHangulOverride(reading) {
  return dictionaryIndex.findHangulOverride(reading);
}

function findHangulOverrideAt(text, index) {
  return dictionaryIndex.findHangulOverrideAt(text, index);
}

function updateLomariPreview() {
  // Lomari always follows the Taipei display convention. Sandhi selection affects audio only.
  lomariPreview.textContent = lomariRenderer.render(imeText.value);
  lomariPreview.scrollTop = lomariPreview.scrollHeight;
}

function audioPlanFromText(text) {
  return audioPlanner.plan(text);
}

function updateAudioButton(playing) {
  audioButton.setAttribute("aria-label", playing ? "Stop audio" : "Play audio");
  audioButton.setAttribute("title", playing ? "Stop" : "Listen");
  audioButton.classList.toggle("playing", playing);
}

async function playPadAudio() {
  if (audioPlayer.isPlaying()) {
    audioPlayer.stop();
    updateAudioButton(false);
    return;
  }

  const content = imeText.value;
  if (!content.trim()) {
    showToast("No text to play");
    return;
  }

  const { segments, missing } = audioPlanFromText(content);
  if (!segments.length) {
    const message = missing.length ? `No audio for: ${missing.join(", ")}` : "No audible syllables to play";
    statusLine.textContent = message;
    statusLine.hidden = false;
    showToast(message);
    return;
  }

  updateAudioButton(true);
  try {
    const completed = await audioPlayer.play(segments);
    if (!completed) return;
    if (missing.length) {
      const message = `Missing audio: ${missing.join(", ")}`;
      statusLine.textContent = message;
      statusLine.hidden = false;
      showToast(message);
    }
  } catch {
    showToast("Could not play audio");
  } finally {
    if (!audioPlayer.isPlaying()) updateAudioButton(false);
  }
}

function setSandhiMode(mode) {
  state.sandhiMode = mode === "singapore" ? "singapore" : "taipei";
  taipeiButton.classList.toggle("active", state.sandhiMode === "taipei");
  singaporeButton.classList.toggle("active", state.sandhiMode === "singapore");
  taipeiButton.setAttribute("aria-pressed", String(state.sandhiMode === "taipei"));
  singaporeButton.setAttribute("aria-pressed", String(state.sandhiMode === "singapore"));
  updateLomariPreview();
}

async function loadDictionary() {
  try {
    const response = await fetch(DATA_URL, { cache: "no-cache" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    setEntries(data.entries || []);
    state.unitRoman = new Map(Object.entries(data.runtime?.unitRoman || {}));
    state.rawHangulAudio = new Map(Object.entries(data.runtime?.rawHangulAudio || {}));
    state.jamoLomari = new Map(Object.entries(data.runtime?.jamoLomari || {}));
    state.jamoAudio = new Map(Object.entries(data.runtime?.jamoAudio || {}));
    imeController.setEntries(state.entries, dictionaryIndex);
    updateLomariPreview();
    // A successful load is the normal state, so keep the toolbar quiet.
    statusLine.textContent = "";
    statusLine.hidden = true;
  } catch {
    statusLine.textContent = "Dictionary candidates unavailable; Hangul typing still works";
    statusLine.hidden = false;
  }
}

clearButton.addEventListener("click", () => {
  imeController.clear();
});

copyButton.addEventListener("click", async () => {
  try {
    await copyText(imeText.value);
    showToast("Copied");
  } catch {
    showToast("Could not copy");
  }
});

audioButton.addEventListener("click", playPadAudio);
taipeiButton.addEventListener("click", () => setSandhiMode("taipei"));
singaporeButton.addEventListener("click", () => setSandhiMode("singapore"));

keyboardGuideButton.addEventListener("click", () => {
  const opening = keyboardGuide.hidden;
  keyboardGuide.hidden = !opening;
  pad?.classList.toggle("keyboard-guide-open", opening);
  keyboardGuideButton.setAttribute("aria-expanded", String(opening));
  keyboardGuideButton.querySelector(".guide-chevron").textContent = opening ? "▲" : "▼";
  if (opening) imeText.focus();
});

imeText.addEventListener("keydown", (event) => {
  const key = physicalGuideKey(event);
  if (key) setGuidePressed(key, true);
  if (event.key === "Shift" && !guideShifted) {
    guideShifted = true;
    refreshGuideShiftState();
  }
});

imeText.addEventListener("keyup", (event) => {
  const key = physicalGuideKey(event);
  if (key) setGuidePressed(key, false);
  if (event.key === "Shift" && guideShifted) {
    guideShifted = false;
    refreshGuideShiftState();
  }
});

if (typeof window.addEventListener === "function") {
  window.addEventListener("blur", () => {
    guideShifted = false;
    for (const key of guideButtons.keys()) setGuidePressed(key, false);
    refreshGuideShiftState();
  });
}

renderKeyboardGuide();

loadDictionary();
