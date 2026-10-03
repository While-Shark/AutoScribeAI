const samples = {
  "uptime-kuma": {
    title: "Uptime Kuma · 简体中文",
    html: "/manuals/uptime-kuma/index.html",
    docx: "/manuals/uptime-kuma/manual.docx"
  },
  "changedetection": {
    title: "changedetection.io · 日本語",
    html: "/manuals/changedetection/index.html",
    docx: "/manuals/changedetection/manual.docx"
  },
  "it-tools": {
    title: "IT Tools · 한국어",
    html: "/manuals/it-tools/index.html",
    docx: "/manuals/it-tools/manual.docx"
  }
};

const dialog = document.querySelector("#preview-dialog");
const frame = document.querySelector("#preview-frame");
const title = document.querySelector("#preview-title");
const kind = document.querySelector("#preview-kind");
const direct = document.querySelector("#preview-direct");
const close = document.querySelector("#preview-close");
const loading = document.querySelector("#preview-loading");

function absoluteUrl(path) {
  return new URL(path, window.location.origin).href;
}

function openPreview(sampleKey, type) {
  const sample = samples[sampleKey];
  if (!sample) return;

  title.textContent = sample.title;
  loading.hidden = false;

  if (type === "word") {
    const fileUrl = absoluteUrl(sample.docx);
    const viewerUrl = "https://view.officeapps.live.com/op/embed.aspx?src=" + encodeURIComponent(fileUrl);
    kind.textContent = "Generated Word document";
    direct.textContent = "Download DOCX ↗";
    direct.href = sample.docx;
    frame.src = viewerUrl;
  } else {
    kind.textContent = "Interactive HTML manual";
    direct.textContent = "Open full page ↗";
    direct.href = sample.html;
    frame.src = sample.html;
  }

  dialog.showModal();
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("[data-preview]");
  if (!target) return;
  openPreview(target.dataset.sample, target.dataset.preview);
});

frame.addEventListener("load", () => {
  loading.hidden = true;
});

close.addEventListener("click", () => {
  dialog.close();
});

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

dialog.addEventListener("close", () => {
  frame.src = "about:blank";
  direct.href = "#";
  loading.hidden = true;
});
