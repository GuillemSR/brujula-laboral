const form = document.querySelector("#ask-form");
const question = document.querySelector("#question");
const result = document.querySelector("#result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.textContent = "Consultando...";

  const button = form.querySelector("button");
  button.disabled = true;

  try {
    const response = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question.value }),
    });

    const payload = await response.json();
    result.textContent = payload.answer || "No se recibio respuesta.";
  } catch (error) {
    result.textContent = "No se pudo conectar con el backend local.";
  } finally {
    button.disabled = false;
  }
});
