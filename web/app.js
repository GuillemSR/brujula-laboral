const askForm = document.querySelector("#ask-form");
const question = document.querySelector("#question");
const result = document.querySelector("#result");
const askButton = document.querySelector("#ask-button");
const questionCount = document.querySelector("#question-count");
const documentFile = document.querySelector("#document-file");
const uploadButton = document.querySelector("#upload-button");
const documentStatus = document.querySelector("#document-status");

let activeDocument = null;

function setBusy(button, isBusy, label) {
  if (!button.dataset.defaultLabel) {
    button.dataset.defaultLabel = button.textContent;
  }
  button.disabled = isBusy;
  button.setAttribute("aria-busy", String(isBusy));
  button.textContent = isBusy ? label : button.dataset.defaultLabel;
}

async function readJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return {};
  }
}

function errorMessage(payload, fallback) {
  return typeof payload.detail === "string" ? payload.detail : fallback;
}

function clear(node) {
  node.replaceChildren();
}

function paragraph(className, text) {
  const element = document.createElement("p");
  element.className = className;
  element.textContent = text;
  return element;
}

function formatBytes(sizeBytes) {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }
  if (sizeBytes < 1024 * 1024) {
    return `${(sizeBytes / 1024).toFixed(1)} KB`;
  }
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function syncQuestionCount() {
  questionCount.textContent = `${question.value.length} / ${question.maxLength}`;
}

function showResult() {
  result.hidden = false;
}

function renderLoading() {
  showResult();
  clear(result);
  const title = document.createElement("h2");
  title.textContent = "Consultando";
  result.append(title, paragraph("", "Preparando respuesta..."));
}

function appendList(parent, title, items, ordered = false) {
  const section = document.createElement("section");
  section.className = "meta-section";
  const heading = document.createElement("h3");
  heading.textContent = title;
  const list = document.createElement(ordered ? "ol" : "ul");

  items.forEach((itemText) => {
    const item = document.createElement("li");
    item.textContent = itemText;
    list.append(item);
  });

  section.append(heading, list);
  parent.append(section);
}

function appendResultMeta(parent, sources) {
  const sourceItems = sources.length
    ? sources.map((source) => {
        const reference = source.reference ? ` ${source.reference}` : "";
        const url = source.url ? ` - ${source.url}` : "";
        return `${source.title || "Fuente sin titulo"}${reference}${url}`;
      })
    : ["Sin fuentes relevantes para esta consulta."];

  appendList(parent, "Fuentes consultadas", sourceItems, sources.length > 0);
}

function renderAnswer(payload) {
  showResult();
  clear(result);

  const title = document.createElement("h2");
  title.textContent = "Respuesta";
  result.append(title, paragraph("answer-text", payload.answer || "No se recibio respuesta."));

  const meta = document.createElement("div");
  meta.className = "meta";

  const sources = Array.isArray(payload.sources) ? payload.sources : [];
  appendResultMeta(meta, sources);
  result.append(meta);
}

function renderStreamingAnswerStart() {
  showResult();
  clear(result);

  const title = document.createElement("h2");
  title.textContent = "Respuesta";
  const answer = paragraph("answer-text", "");
  const meta = document.createElement("div");
  meta.className = "meta";

  result.append(title, answer, meta);
  return { answer, meta };
}

function renderError(message) {
  showResult();
  clear(result);
  const title = document.createElement("h2");
  title.textContent = "Error";
  result.append(title, paragraph("error", message));
}

async function deleteTemporaryDocument(documentId) {
  try {
    await fetch(`/documents/${documentId}`, { method: "DELETE" });
  } catch (error) {
    // El lifecycle del almacenamiento temporal queda como red de seguridad.
  }
}

function renderDocumentStatus(message) {
  clear(documentStatus);

  if (!activeDocument) {
    documentStatus.textContent = message || "Sin documento adjunto.";
    return;
  }

  const summary = document.createElement("div");
  summary.className = "document-summary";
  const text = document.createElement("div");
  const filename = document.createElement("strong");
  filename.textContent = activeDocument.filename;
  const details = document.createElement("span");
  details.textContent = `${formatBytes(activeDocument.size_bytes)} - caduca en ${
    activeDocument.expires_in_minutes
  } min`;
  text.append(filename, details);

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "secondary";
  remove.textContent = "Quitar";
  remove.addEventListener("click", removeActiveDocument);

  summary.append(text, remove);
  documentStatus.append(summary);
}

async function removeActiveDocument() {
  if (!activeDocument) {
    renderDocumentStatus();
    return;
  }

  const documentId = activeDocument.document_id;
  activeDocument = null;
  documentFile.value = "";
  renderDocumentStatus("Quitando documento temporal...");
  await deleteTemporaryDocument(documentId);
  renderDocumentStatus();
}

function handleStreamEvent(event, streamState) {
  if (event.type === "meta") {
    const sources = Array.isArray(event.sources) ? event.sources : [];
    clear(streamState.meta);
    appendResultMeta(streamState.meta, sources);
    return;
  }

  if (event.type === "chunk") {
    streamState.answer.textContent += event.text || "";
    return;
  }

  if (event.type === "error") {
    throw new Error(event.detail || "No se pudo completar la respuesta en streaming.");
  }
}

function parseStreamLine(line, streamState) {
  const trimmed = line.trim();
  if (!trimmed) {
    return;
  }
  handleStreamEvent(JSON.parse(trimmed), streamState);
}

async function readStreamingAnswer(response, streamState) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    lines.forEach((line) => parseStreamLine(line, streamState));
  }

  buffer += decoder.decode();
  parseStreamLine(buffer, streamState);
  if (!streamState.answer.textContent.trim()) {
    streamState.answer.textContent = "No se recibio respuesta.";
  }
}

question.addEventListener("input", syncQuestionCount);

uploadButton.addEventListener("click", () => {
  documentFile.click();
});

documentFile.addEventListener("change", async () => {
  if (!documentFile.files.length) {
    return;
  }

  setBusy(uploadButton, true, "Subiendo...");
  documentStatus.textContent = "Subiendo documento...";

  try {
    const body = new FormData();
    body.append("file", documentFile.files[0]);
    const response = await fetch("/documents", { method: "POST", body });
    const payload = await readJson(response);

    if (!response.ok) {
      documentStatus.textContent = errorMessage(payload, "No se pudo subir el documento.");
      return;
    }

    const previousDocumentId = activeDocument?.document_id;
    activeDocument = payload;
    renderDocumentStatus();

    if (previousDocumentId && previousDocumentId !== activeDocument.document_id) {
      await deleteTemporaryDocument(previousDocumentId);
    }
  } catch (error) {
    documentStatus.textContent = "No se pudo conectar con el backend local.";
  } finally {
    setBusy(uploadButton, false);
  }
});

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setBusy(askButton, true, "Enviando...");

  const body = { question: question.value };
  if (activeDocument) {
    body.document_id = activeDocument.document_id;
  }

  try {
    renderLoading();
    const response = await fetch("/ask/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const payload = await readJson(response);
      renderError(errorMessage(payload, "No se pudo obtener una respuesta."));
      return;
    }

    if (!response.body) {
      const payload = await readJson(response);
      renderAnswer(payload);
      return;
    }

    const streamState = renderStreamingAnswerStart();
    await readStreamingAnswer(response, streamState);
  } catch (error) {
    renderError(error.message || "No se pudo conectar con el backend local.");
  } finally {
    setBusy(askButton, false);
  }
});

syncQuestionCount();
