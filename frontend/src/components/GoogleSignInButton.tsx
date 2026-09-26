import { useEffect, useRef } from "react";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string;
const API_URL = (import.meta.env.VITE_API_URL as string) ?? "http://localhost:8000";

export interface GoogleUser {
  id: string;
  google_sub: string;
  email: string;
  name: string;
  picture: string | null;
}

interface GoogleSignInButtonProps {
  onSuccess?: (user: GoogleUser) => void;
  onError?: (error: Error) => void;
}

// Tipado mínimo del SDK de Google Identity Services (window.google.accounts.id).
// El SDK no publica @types oficiales; esto evita usar `any` suelto en el resto del componente.
interface GoogleIdConfiguration {
  client_id: string;
  callback: (response: { credential: string }) => void;
  ux_mode?: "popup" | "redirect";
}
interface GoogleButtonOptions {
  type?: "standard" | "icon";
  theme?: "outline" | "filled_blue" | "filled_black";
  size?: "small" | "medium" | "large";
  text?: "signin_with" | "signup_with" | "continue_with" | "signin";
  shape?: "rectangular" | "pill" | "circle" | "square";
  logo_alignment?: "left" | "center";
}
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: GoogleIdConfiguration) => void;
          renderButton: (parent: HTMLElement, options: GoogleButtonOptions) => void;
        };
      };
    };
  }
}

export default function GoogleSignInButton({ onSuccess, onError }: GoogleSignInButtonProps) {
  const buttonRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // El script https://accounts.google.com/gsi/client debe estar en index.html.
    if (!window.google || !buttonRef.current) {
      console.error(
        "El script de Google Identity Services no está cargado. " +
        'Agrega <script src="https://accounts.google.com/gsi/client" async defer></script> a index.html'
      );
      return;
    }

    async function handleCredentialResponse(response: { credential: string }) {
      // response.credential es el id_token (JWT) firmado por Google.
      // Nunca se decodifica ni confía en el frontend: se envía tal cual al backend,
      // que hace la verificación criptográfica real.
      try {
        const res = await fetch(`${API_URL}/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ credential: response.credential }),
        });

        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.detail ?? `Error ${res.status} al autenticar`);
        }

        const user: GoogleUser = await res.json();
        onSuccess?.(user);
      } catch (err) {
        onError?.(err as Error);
      }
    }

    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleCredentialResponse,
      ux_mode: "popup",
    });

    window.google.accounts.id.renderButton(buttonRef.current, {
      type: "standard",
      theme: "outline",
      size: "large",
      text: "signin_with",
      shape: "rectangular",
      logo_alignment: "left",
    });
  }, [onSuccess, onError]);

  return <div ref={buttonRef} />;
}