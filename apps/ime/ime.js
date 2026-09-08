const DATA_URL = "/public/data/hokkien-hanri-dict.json";

const imeText = document.querySelector("#imeText");
const clearButton = document.querySelector("#clearButton");
const copyButton = document.querySelector("#copyButton");
const audioButton = document.querySelector("#audioButton");
const taipeiButton = document.querySelector("#taipeiButton");
const singaporeButton = document.querySelector("#singaporeButton");
const candidateBar = document.querySelector("#candidateBar");
const statusLine = document.querySelector("#statusLine");
const toast = document.querySelector("#toast");

const imeCore = window.TangliengimImeCore;
const imeController = imeCore.createTextImeController({
  control: imeText,
  candidateContainer: candidateBar,
  enabled: () => true,
  enterBehavior: "newline",
});

const state = {
  entries: [],
  hanriEntries: [],
  readingEntries: new Map(),
  sandhiMode: "taipei",
};
let audioRunId = 0;
let currentAudio = null;
let sharedAudioContext = null;
const decodedAudioCache = new Map();

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

  for (const entry of state.entries) {
    addReadingEntry(entry.readingBase, entry);
    addReadingEntry(entry.reading, entry);
    addReadingEntry(entry.raw?.reading, entry);
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
    statusLine.textContent = `${data.counts?.active_entries || data.entries?.length || 0} dictionary entries loaded`;
  } catch {
    statusLine.textContent = "Dictionary candidates unavailable; Hangul typing still works";
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

loadDictionary();
