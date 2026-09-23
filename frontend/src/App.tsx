import { useState } from "react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const sendPrompt = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://localhost:8000/students/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
        }),
      });

      const data = await res.json();

      setResponse(data.response);
    } catch (error) {
      console.error(error);
      setResponse("Error conectando con el backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "40px auto", padding: "20px" }}>
      <h1>Adaptive Driving Tutor</h1>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Escribe un prompt..."
        rows={5}
        style={{ width: "100%", marginBottom: "10px" }}
      />

      <button onClick={sendPrompt} disabled={loading}>
        {loading ? "Generando..." : "Enviar"}
      </button>

      <h2>Respuesta</h2>

      <pre
        style={{
          whiteSpace: "pre-wrap",
          background: "#f4f4f4",
          padding: "15px",
          minHeight: "100px",
        }}
      >
        {response}
      </pre>
    </div>
  );
}

export default App;