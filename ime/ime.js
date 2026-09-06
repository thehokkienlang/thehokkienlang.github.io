const DATA_URL = "/dictionary/public/data/hokkien-hanri-dict.json?v=20260906-new-tsv-rows";

const imeText = document.querySelector("#imeText");
const clearButton = document.querySelector("#clearButton");
const copyButton = document.querySelector("#copyButton");
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

async function loadDictionary() {
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    imeController.setEntries(data.entries || []);
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

loadDictionary();
