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
const lomariCore = window.TangliengimLomariPreview;
const imeController = imeCore.createTextImeController({
  control: imeText,
  candidateContainer: candidateBar,
  enabled: () => true,
  onUpdate: updateLomariPreview,
  enterBehavior: "newline",
});

const state = {
  entries: [],
  hanriEntries: [],
  hangulOverrides: new Map(),
  readingEntries: new Map(),
  sandhiMode: "taipei",
};
const lomariRenderer = lomariCore.createRenderer({
  imeCore,
  findHanriEntry,
  findHangulOverride,
});
let audioRunId = 0;
let currentAudio = null;
let sharedAudioContext = null;
const decodedAudioCache = new Map();
const guideButtons = new Map();
let guideShifted = false;

const GUIDE_ROWS = [
  ["1", "2", "4", "5"],
  [..."qwertyuiop"],
  [..."asdfghjkl"],
  [..."zxcvbnm"],
  ["Shift", "Space", "’", "Backspace"],
];

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
    button.textContent = key;
  } else if (key === "’") {
    button.classList.add("control-key", "key-apostrophe");
    button.textContent = key;
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

function textAreaCaretPosition(control) {
  if (!document.body || typeof getComputedStyle !== "function") return null;
  const style = getComputedStyle(control);
  const mirror = document.createElement("div");
  const properties = [
    "boxSizing", "fontFamily", "fontSize", "fontWeight", "fontStyle", "letterSpacing", "lineHeight",
    "textTransform", "textIndent", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
    "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth",
  ];
  mirror.style.position = "fixed";
  mirror.style.visibility = "hidden";
  mirror.style.pointerEvents = "none";
  mirror.style.whiteSpace = "pre-wrap";
  mirror.style.overflowWrap = "break-word";
  mirror.style.width = `${control.offsetWidth}px`;
  for (const property of properties) mirror.style[property] = style[property];
  const cursor = control.selectionStart ?? 0;
  mirror.textContent = control.value.slice(0, cursor);
  const marker = document.createElement("span");
  marker.textContent = control.value.slice(cursor, cursor + 1) || "\u200b";
  mirror.append(marker);
  document.body.append(mirror);
  const position = {
    left: marker.offsetLeft - control.scrollLeft,
    top: marker.offsetTop - control.scrollTop,
    height: Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.4,
  };
  mirror.remove();
  return position;
}

function positionCandidatePopup() {
  if (candidateBar.hidden || !candidateBar.children.length || !textWrap) return;
  const caret = textAreaCaretPosition(imeText);
  if (!caret) return;
  const maximumLeft = Math.max(8, textWrap.clientWidth - candidateBar.offsetWidth - 8);
  candidateBar.style.left = `${Math.max(8, Math.min(caret.left, maximumLeft))}px`;
  let top = caret.top + caret.height + 4;
  if (top + candidateBar.offsetHeight > imeText.clientHeight && caret.top > candidateBar.offsetHeight + 8) {
    top = caret.top - candidateBar.offsetHeight - 4;
  }
  candidateBar.style.top = `${Math.max(4, top)}px`;
}

function scheduleCandidatePopupPosition() {
  const schedule = typeof requestAnimationFrame === "function" ? requestAnimationFrame : setTimeout;
  schedule(positionCandidatePopup);
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

function normalizeAudioSegments(audio) {
  if (audio?.segments?.length) {
    return audio.segments;
  }
  return (audio?.files || []).map((file) => ({
    file,
    trimStart: false,
    trimEnd: false,
    speed: 1,
    lFinal: false,
    shortOverlapFinal: false,
    englishClusterHelper: false,
  }));
}

function audioForCurrentSandhiMode(audio) {
  if (state.sandhiMode === "singapore" && audio?.singapore) {
    return audio.singapore;
  }
  return audio;
}

function dictionaryAudioPath(file) {
  const value = String(file || "");
  if (!value) return "";
  if (/^https?:\/\//i.test(value) || value.startsWith("/")) return value;
  return `/${value}`;
}

function entrySegments(entry) {
  return normalizeAudioSegments(audioForCurrentSandhiMode(entry.audio)).map((segment) => ({
    ...segment,
    file: dictionaryAudioPath(segment.file),
  }));
}

function addReadingEntry(key, entry) {
  if (!key) return;
  const normalized = imeCore.normalizeText(TangliengimHangulIme.normalizeReadingBase(key));
  if (!normalized) return;
  if (!state.readingEntries.has(normalized)) {
    state.readingEntries.set(normalized, []);
  }
  state.readingEntries.get(normalized).push(entry);
}

function searchableEntry(entry) {
  return entry.active && entry.kind !== "numeric_override";
}

function setEntries(entries) {
  state.entries = (entries || []).filter(searchableEntry);
  state.hanriEntries = state.entries
    .filter((entry) => entry.hanri && entry.kind !== "hangul_override")
    .sort((a, b) =>
      [...b.hanri].length - [...a.hanri].length ||
      a.priority - b.priority ||
      a.row - b.row
    );
  state.readingEntries = new Map();
  state.hangulOverrides = new Map();

  for (const entry of state.entries) {
    addReadingEntry(entry.readingBase, entry);
    addReadingEntry(entry.reading, entry);
    addReadingEntry(entry.raw?.reading, entry);
    if (entry.kind === "hangul_override") {
      const key = imeCore.normalizeText(TangliengimHangulIme.normalizeReadingBase(entry.readingBase));
      if (key && !state.hangulOverrides.has(key)) state.hangulOverrides.set(key, entry);
    }
  }

  for (const candidates of state.readingEntries.values()) {
    candidates.sort((a, b) =>
      a.priority - b.priority ||
      a.row - b.row ||
      String(a.hanri || "").localeCompare(String(b.hanri || ""))
    );
  }
}

function isPunctuationOrSpace(char) {
  return /\s|\p{Punctuation}/u.test(char);
}

function findHanriEntry(text, index) {
  for (const entry of state.hanriEntries) {
    if (text.startsWith(entry.hanri, index)) {
      return entry;
    }
  }
  return null;
}

function findReadingEntry(reading) {
  const key = imeCore.normalizeText(TangliengimHangulIme.normalizeReadingBase(reading));
  return state.readingEntries.get(key)?.[0] || null;
}

function findHangulOverride(reading) {
  const key = imeCore.normalizeText(TangliengimHangulIme.normalizeReadingBase(reading));
  return state.hangulOverrides.get(key) || null;
}

function updateLomariPreview() {
  lomariPreview.textContent = lomariRenderer.render(imeText.value, state.sandhiMode);
  lomariPreview.scrollTop = lomariPreview.scrollHeight;
  scheduleCandidatePopupPosition();
}

function appendEntryAudio(entry, segments, missing) {
  const audio = audioForCurrentSandhiMode(entry.audio);
  const audioSegments = entrySegments(entry);
  if (audioSegments.length) {
    segments.push(...audioSegments);
  }
  for (const item of audio?.missing || []) {
    if (!missing.includes(item)) missing.push(item);
  }
}

function audioPlanFromText(text) {
  const segments = [];
  const missing = [];
  let index = 0;

  while (index < text.length) {
    const code = text.codePointAt(index);
    if (code === undefined) break;
    const char = String.fromCodePoint(code);

    if (isPunctuationOrSpace(char)) {
      index += char.length;
      continue;
    }

    const hanriEntry = findHanriEntry(text, index);
    if (hanriEntry) {
      appendEntryAudio(hanriEntry, segments, missing);
      index += hanriEntry.hanri.length;
      continue;
    }

    const unit = imeCore.readingUnitAt(text, index);
    if (unit?.canCarryTone) {
      const end = imeCore.readingUnitToneEnd(text, unit);
      const raw = text.slice(index, end);
      const entry = findReadingEntry(raw) || findReadingEntry(unit.text);
      if (entry) {
        appendEntryAudio(entry, segments, missing);
      } else if (!missing.includes(raw)) {
        missing.push(raw);
      }
      index = end;
      continue;
    }

    if (/[A-Za-z0-9]/.test(char)) {
      let end = index + char.length;
      while (end < text.length) {
        const next = String.fromCodePoint(text.codePointAt(end));
        if (!/[A-Za-z0-9]/.test(next)) break;
        end += next.length;
      }
      const word = text.slice(index, end);
      if (!missing.includes(word)) missing.push(word);
      index = end;
      continue;
    }

    if (!missing.includes(char)) missing.push(char);
    index += char.length;
  }

  return { segments, missing };
}

function stopAudio() {
  audioRunId += 1;
  if (currentAudio) {
    try {
      currentAudio.stop();
    } catch {
      // The source may already have ended.
    }
    currentAudio = null;
  }
}

function audioContext() {
  if (!sharedAudioContext) {
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!Context) {
      throw new Error("Web Audio is not available");
    }
    sharedAudioContext = new Context();
  }
  return sharedAudioContext;
}

async function decodedAudioBuffer(file) {
  const url = encodeURI(file);
  if (decodedAudioCache.has(url)) {
    return decodedAudioCache.get(url);
  }

  const bufferPromise = fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.arrayBuffer();
    })
    .then((arrayBuffer) => audioContext().decodeAudioData(arrayBuffer));
  decodedAudioCache.set(url, bufferPromise);
  return bufferPromise;
}

function copyBufferChannels(buffer, startFrame, endFrame) {
  const length = Math.max(1, endFrame - startFrame);
  const channels = [];
  for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
    channels.push(buffer.getChannelData(channel).slice(startFrame, startFrame + length));
  }
  return channels;
}

function crossfadeSamples(previous, next) {
  const length = Math.min(previous.length, next.length);
  const output = new Float32Array(length);
  if (length <= 1) {
    output.set(next.subarray(0, length));
    return output;
  }
  for (let index = 0; index < length; index += 1) {
    const alpha = index / (length - 1);
    output[index] = previous[index] * (1 - alpha) + next[index] * alpha;
  }
  return output;
}

function speedUpChannels(channels, sampleRate, speedFactor) {
  if (speedFactor <= 1 || !channels.length || !sampleRate) {
    return channels;
  }

  const totalFrames = channels[0].length;
  if (totalFrames <= sampleRate / 20) {
    return channels;
  }

  const keepFrames = Math.max(1, Math.round(sampleRate * 0.1));
  const removeFrames = Math.max(1, Math.round(keepFrames * (speedFactor - 1)));
  const fadeFrames = Math.max(1, Math.round(sampleRate * 0.01));
  const output = channels.map(() => []);
  let position = 0;

  while (position < totalFrames) {
    const keepEnd = Math.min(position + keepFrames, totalFrames);
    for (let channel = 0; channel < channels.length; channel += 1) {
      const source = channels[channel];
      const target = output[channel];
      for (let sample = position; sample < keepEnd; sample += 1) {
        target.push(source[sample]);
      }
    }
    position = keepEnd;

    if (position >= totalFrames) break;
    const skipEnd = Math.min(position + removeFrames, totalFrames);
    const canCrossfade = output[0].length >= fadeFrames && skipEnd + fadeFrames < totalFrames;

    if (canCrossfade) {
      for (let channel = 0; channel < channels.length; channel += 1) {
        const target = output[channel];
        const source = channels[channel];
        const targetStart = target.length - fadeFrames;
        for (let sample = 0; sample < fadeFrames; sample += 1) {
          const alpha = sample / Math.max(1, fadeFrames - 1);
          target[targetStart + sample] =
            target[targetStart + sample] * (1 - alpha) + source[skipEnd + sample] * alpha;
        }
      }
      position = skipEnd + fadeFrames;
    } else {
      position = skipEnd;
    }
  }

  return output.map((channel) => Float32Array.from(channel));
}

function fadeOutChannels(channels, sampleRate, fadeSeconds) {
  const fadeFrames = Math.min(
    channels[0]?.length || 0,
    Math.max(1, Math.round(sampleRate * fadeSeconds))
  );
  if (fadeFrames <= 1) return channels;

  for (const channel of channels) {
    const start = channel.length - fadeFrames;
    for (let index = 0; index < fadeFrames; index += 1) {
      channel[start + index] *= (fadeFrames - index - 1) / (fadeFrames - 1);
    }
  }
  return channels;
}

function audioTrimFrames(buffer, segment) {
  let startSeconds = 0;
  if (segment.englishClusterHelper) {
    startSeconds = 0.24;
  } else if (segment.trimStart) {
    startSeconds = 0.2;
  }
  const endSeconds = segment.trimEnd ? 0.15 : 0;
  let startFrame = Math.round(buffer.sampleRate * startSeconds);
  let endFrame = buffer.length - Math.round(buffer.sampleRate * endSeconds);

  if (startFrame >= endFrame) {
    const overflow = startFrame - endFrame + 1;
    const endTrimFrames = buffer.length - endFrame;
    if (endTrimFrames >= overflow) {
      endFrame += overflow;
    } else {
      startFrame = Math.max(0, startFrame - (overflow - endTrimFrames));
      endFrame = buffer.length;
    }
  }

  return {
    startFrame: Math.max(0, Math.min(startFrame, buffer.length - 1)),
    endFrame: Math.max(1, Math.min(endFrame, buffer.length)),
  };
}

async function processedAudioSegment(segment) {
  const buffer = await decodedAudioBuffer(segment.file);
  const { startFrame, endFrame } = audioTrimFrames(buffer, segment);
  let channels = copyBufferChannels(buffer, startFrame, endFrame);
  channels = speedUpChannels(channels, buffer.sampleRate, Number(segment.speed) || 1);

  if (segment.englishClusterHelper && channels[0]?.length) {
    const maxFrames = Math.max(1, Math.round(buffer.sampleRate * 0.24));
    channels = channels.map((channel) => channel.slice(0, Math.min(channel.length, maxFrames)));
    fadeOutChannels(channels, buffer.sampleRate, 0.015);
  }

  return {
    channels,
    sampleRate: buffer.sampleRate,
    channelCount: buffer.numberOfChannels,
    canOverlapPrevious: Boolean(segment.trimStart),
    lFinal: Boolean(segment.lFinal),
    shortOverlapFinal: Boolean(segment.shortOverlapFinal),
    englishClusterHelper: Boolean(segment.englishClusterHelper),
  };
}

function overlapSeconds(previous, current) {
  if (current.englishClusterHelper) return 0.04;
  if (previous.englishClusterHelper) return 0.04;
  if (previous.shortOverlapFinal) return 0.05;
  if (previous.lFinal) return 0.15;
  return 0.1;
}

function appendChannels(previousChannels, nextChannels, overlapFrames) {
  const channelCount = previousChannels.length;
  const previousLength = previousChannels[0].length;
  const nextLength = nextChannels[0].length;
  const overlap = Math.max(0, Math.min(overlapFrames, previousLength, nextLength));
  const outputLength = previousLength + nextLength - overlap;
  const outputChannels = [];

  for (let channel = 0; channel < channelCount; channel += 1) {
    const previous = previousChannels[channel];
    const next = nextChannels[Math.min(channel, nextChannels.length - 1)];
    const output = new Float32Array(outputLength);
    output.set(previous.subarray(0, previousLength - overlap), 0);
    if (overlap > 0) {
      output.set(
        crossfadeSamples(previous.subarray(previousLength - overlap), next.subarray(0, overlap)),
        previousLength - overlap
      );
    }
    output.set(next.subarray(overlap), previousLength);
    outputChannels.push(output);
  }

  return outputChannels;
}

async function buildImeAudioBuffer(segments) {
  const context = audioContext();
  const processed = [];
  for (const segment of segments) {
    processed.push(await processedAudioSegment(segment));
  }
  if (!processed.length) {
    throw new Error("No playable audio");
  }

  const sampleRate = processed[0].sampleRate;
  const channelCount = processed[0].channelCount;
  const leadFrames = Math.max(0, Math.round(sampleRate * 0.25));
  let combined = Array.from({ length: channelCount }, () => new Float32Array(leadFrames));
  let previousSegment = null;

  for (const segment of processed) {
    if (segment.sampleRate !== sampleRate || segment.channelCount !== channelCount) {
      throw new Error("Audio files use different formats");
    }

    const overlap = previousSegment && segment.canOverlapPrevious
      ? Math.round(sampleRate * overlapSeconds(previousSegment, segment))
      : 0;
    combined = appendChannels(combined, segment.channels, overlap);
    previousSegment = segment;
  }

  const output = context.createBuffer(channelCount, combined[0].length, sampleRate);
  for (let channel = 0; channel < channelCount; channel += 1) {
    output.copyToChannel(combined[channel], channel);
  }
  return output;
}

function updateAudioButton(playing) {
  audioButton.setAttribute("aria-label", playing ? "Stop audio" : "Play audio");
  audioButton.setAttribute("title", playing ? "Stop" : "Listen");
  audioButton.classList.toggle("playing", playing);
}

async function playPadAudio() {
  if (currentAudio) {
    stopAudio();
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

  stopAudio();
  const runId = audioRunId;
  updateAudioButton(true);
  try {
    const context = audioContext();
    await context.resume();
    const buffer = await buildImeAudioBuffer(segments);
    if (runId !== audioRunId) return;

    await new Promise((resolve) => {
      const source = context.createBufferSource();
      source.buffer = buffer;
      source.connect(context.destination);
      source.addEventListener("ended", resolve, { once: true });
      currentAudio = source;
      source.start();
    });

    if (missing.length) {
      const message = `Missing audio: ${missing.join(", ")}`;
      statusLine.textContent = message;
      statusLine.hidden = false;
      showToast(message);
    }
  } catch {
    showToast("Could not play audio");
  } finally {
    if (runId === audioRunId) {
      currentAudio = null;
      updateAudioButton(false);
    }
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
    imeController.setEntries(state.entries);
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
  scheduleCandidatePopupPosition();
});

imeText.addEventListener("scroll", scheduleCandidatePopupPosition);
imeText.addEventListener("click", scheduleCandidatePopupPosition);
if (typeof window.addEventListener === "function") {
  window.addEventListener("resize", scheduleCandidatePopupPosition);
  window.addEventListener("blur", () => {
    guideShifted = false;
    for (const key of guideButtons.keys()) setGuidePressed(key, false);
    refreshGuideShiftState();
  });
}

renderKeyboardGuide();

loadDictionary();
