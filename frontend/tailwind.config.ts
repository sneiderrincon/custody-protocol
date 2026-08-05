import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0B0D0F",
        panel: "#14171B",
        accent: "#E8A33D",
        success: "#4C9A6A",
        danger: "#D1665A",
        border: "#252A31",
        muted: "#9AA3AD",
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "ui-sans-serif", "system-ui"],
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "Consolas"],
      },
      borderRadius: {
        lg: "8px",
        md: "7px",
        sm: "6px",
      },
    },
  },
  plugins: [],
};

export default config;
