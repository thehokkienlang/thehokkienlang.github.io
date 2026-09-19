const TangliengimWebAudio = (() => {
  const MULTI_SYLLABLE_SPEED = 1.10;
  const TONE4_SPEED = 1.03;
  const L_FINAL_SPEED = 1.45;
  let sharedAudioContext = null;
  const decodedAudioCache = new Map();

  function audioContext() {
    if (!sharedAudioContext) {
      const Context = window.AudioContext || window.webkitAudioContext;
      if (!Context) throw new Error("Web Audio is not available");
      sharedAudioContext = new Context();
    }
    return sharedAudioContext;
  }

  async function decodedAudioBuffer(file) {
    const url = encodeURI(file);
    if (decodedAudioCache.has(url)) return decodedAudioCache.get(url);
    const bufferPromise = fetch(url)
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.arrayBuffer();
      })
      .then((arrayBuffer) => audioContext().decodeAudioData(arrayBuffer));
    decodedAudioCache.set(url, bufferPromise);
    return bufferPromise;
  }

  function normalizeAudioSegments(audio) {
    if (Array.isArray(audio)) return audio;
    if (audio?.segments?.length) return audio.segments;
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

  function legacyPlaybackSegments(audio) {
    const segments = normalizeAudioSegments(audio).map((segment) => ({ ...segment }));
    if (segments.length <= 1) {
      if (segments[0]) segments[0].speed = 1;
      return segments;
    }
    return segments.map((segment, index) => {
      const previousLFinal = index > 0 && Boolean(segments[index - 1].lFinal);
      const nextLFinal = index + 1 < segments.length && Boolean(segments[index + 1].lFinal);
      let speed = MULTI_SYLLABLE_SPEED;
      if (segment.englishClusterHelper) speed = 1;
      else if (String(segment.tone || "") === "4") speed = TONE4_SPEED;
      else if (segment.lFinal && (previousLFinal || nextLFinal)) speed = L_FINAL_SPEED;
      return { ...segment, speed };
    });
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
    if (speedFactor <= 1 || !channels.length || !sampleRate) return channels;
    const totalFrames = channels[0].length;
    if (totalFrames <= sampleRate / 20) return channels;

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
        for (let sample = position; sample < keepEnd; sample += 1) target.push(source[sample]);
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
    if (segment.englishClusterHelper) startSeconds = 0.24;
    else if (segment.trimStart) startSeconds = 0.2;
    const endSeconds = segment.trimEnd ? 0.15 : 0;
    let startFrame = Math.round(buffer.sampleRate * startSeconds);
    let endFrame = buffer.length - Math.round(buffer.sampleRate * endSeconds);

    if (startFrame >= endFrame) {
      const overflow = startFrame - endFrame + 1;
      const endTrimFrames = buffer.length - endFrame;
      if (endTrimFrames >= overflow) endFrame += overflow;
      else {
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
    if (current.englishClusterHelper || previous.englishClusterHelper) return 0.04;
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

  async function buildAudioBuffer(segments) {
    const context = audioContext();
    const processed = [];
    for (const segment of legacyPlaybackSegments(segments)) {
      processed.push(await processedAudioSegment(segment));
    }
    if (!processed.length) throw new Error("No playable audio");

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

  function createPlayer() {
    let runId = 0;
    let currentSource = null;
    let active = false;

    function stop() {
      runId += 1;
      active = false;
      if (!currentSource) return;
      try {
        currentSource.stop();
      } catch {
        // The source may already have ended.
      }
      currentSource = null;
    }

    async function play(audio) {
      stop();
      const thisRun = runId;
      active = true;
      try {
        const context = audioContext();
        await context.resume();
        const buffer = await buildAudioBuffer(normalizeAudioSegments(audio));
        if (thisRun !== runId) return false;
        await new Promise((resolve) => {
          const source = context.createBufferSource();
          source.buffer = buffer;
          source.connect(context.destination);
          source.addEventListener("ended", resolve, { once: true });
          currentSource = source;
          source.start();
        });
        return thisRun === runId;
      } finally {
        if (thisRun === runId) {
          currentSource = null;
          active = false;
        }
      }
    }

    return {
      isPlaying: () => active,
      play,
      stop,
    };
  }

  return {
    createPlayer,
    legacyPlaybackSegments,
    normalizeAudioSegments,
  };
})();

window.TangliengimWebAudio = TangliengimWebAudio;
