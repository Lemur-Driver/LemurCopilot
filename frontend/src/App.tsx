import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Conectando con el backend...");

  useEffect(() => {
    fetch("http://localhost:8000/")
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message);
      })
      .catch((error) => {
        console.error("Error conectando con FastAPI:", error);
        setMessage("Error conectando con el backend");
      });
  }, []);

  return (
    <div>
      <h1>Adaptive Driving Tutor holaa jeje</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;

