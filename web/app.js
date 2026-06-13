const askForm = document.querySelector("#ask-form");
const question = document.querySelector("#question");
const result = document.querySelector("#result");
const askButton = document.querySelector("#ask-button");
const documentForm = document.querySelector("#document-form");
const documentFile = document.querySelector("#document-file");
const privacyConfirmation = document.querySelector("#privacy-confirmation");
const uploadButton = document.querySelector("#upload-button");
const documentStatus = document.querySelector("#document-status");

let activeDocument = null;

function setBusy(button, isBusy) {
  button.disabled = isBusy;
  button.setAttribute("aria-busy", String(isBusy));
}

function clearNode(node) {
  node.replaceChildren();
}

function appendTextBlock(parent, className, text) {
  const block = document.createElement("p");
  block.className = className;
  block.textContent = text;
  parent.append(block);
}

async function readJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return {};
  }
}

function getErrorMessage(payload, fallback) {
  if (typeof payload.detail === "string") {
    return payload.detail;
  }
  return fallback;
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

function renderDocumentStatus(message) {
  clearNode(documentStatus);

  if (!activeDocument) {
    documentStatus.textContent = message || "No hay documento temporal activo.";
    return;
  }

  const summary = document.createElement("div");
  summary.className = "document-summary";

  const text = document.createElement("span");
  text.textContent = `${activeDocument.filename} · ${formatBytes(
    activeDocument.size_bytes,
  )} · caduca en ${activeDocument.expires_in_minutes} min`;

  const removeButton = document.createElement("button");
  removeButton.type = "button";
  removeButton.className = "secondary-button";
  removeButton.textContent = "Quitar";
  removeButton.addEventListener("click", removeActiveDocument);

  summary.append(text, removeButton);
  documentStatus.append(summary);
}

function renderResult(payload) {
  clearNode(result);

  const answerSection = document.createElement("section");
  answerSection.className = "answer-section";
  const answerTitle = document.createElement("h2");
  answerTitle.textContent = "Respuesta";
  answerSection.append(answerTitle);
  appendTextBlock(answerSection, "answer-text", payload.answer || "No se recibio respuesta.");
  result.append(answerSection);

  if (Array.isArray(payload.sources) && payload.sources.length > 0) {
    const sourcesSection = document.createElement("section");
    sourcesSection.className = "sources-section";
    const sourcesTitle = document.createElement("h2");
    sourcesTitle.textContent = "Fuentes consultadas";
    const sourcesList = document.createElement("ol");

    payload.sources.forEach((source) => {
      const item = document.createElement("li");
      const title = document.createElement(source.url ? "a" : "span");
      title.textContent = source.title || "Fuente sin titulo";
      if (source.url) {
        title.href = source.url;
        title.rel = "noreferrer";
        title.target = "_blank";
      }
      item.append(title);

      if (source.reference) {
        const reference = document.createElement("span");
        reference.className = "source-reference";
        reference.textContent = ` ${source.reference}`;
        item.append(reference);
      }

      sourcesList.append(item);
    });

    sourcesSection.append(sourcesTitle, sourcesList);
    answerSection.append(sourcesSection);
  }
}

function renderError(message) {
  clearNode(result);
  const error = document.createElement("p");
  error.className = "error-message";
  error.textContent = message;
  result.append(error);
}

function syncUploadState() {
  uploadButton.disabled = !privacyConfirmation.checked || !documentFile.files.length;
}

async function deleteTemporaryDocument(documentId) {
  try {
    await fetch(`/documents/${documentId}`, { method: "DELETE" });
  } catch (error) {
    // El lifecycle del bucket sigue siendo la red de seguridad si falla el borrado explicito.
  }
}

privacyConfirmation.addEventListener("change", syncUploadState);
documentFile.addEventListener("change", syncUploadState);

documentForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!privacyConfirmation.checked || !documentFile.files.length) {
    return;
  }

  setBusy(uploadButton, true);
  documentStatus.textContent = "Subiendo documento...";

  try {
    const body = new FormData();
    body.append("file", documentFile.files[0]);

    const response = await fetch("/documents", {
      method: "POST",
      body,
    });

    const payload = await readJson(response);
    if (!response.ok) {
      documentStatus.textContent = getErrorMessage(
        payload,
        "No se pudo subir el documento temporal.",
      );
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
    syncUploadState();
  }
});

async function removeActiveDocument() {
  if (!activeDocument) {
    renderDocumentStatus();
    return;
  }

  const documentId = activeDocument.document_id;
  activeDocument = null;
  documentFile.value = "";
  renderDocumentStatus("Quitando documento temporal...");
  syncUploadState();

  await deleteTemporaryDocument(documentId);
  renderDocumentStatus();
}

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.textContent = "Consultando...";
  setBusy(askButton, true);

  const body = { question: question.value };
  if (activeDocument) {
    body.document_id = activeDocument.document_id;
  }

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const payload = await readJson(response);
    if (!response.ok) {
      renderError(getErrorMessage(payload, "No se pudo obtener una respuesta."));
      return;
    }

    renderResult(payload);
  } catch (error) {
    renderError("No se pudo conectar con el backend local.");
  } finally {
    setBusy(askButton, false);
  }
});
