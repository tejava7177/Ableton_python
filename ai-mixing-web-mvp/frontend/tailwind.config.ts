import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0f141b",
        panel: "#1b2430",
        card: "#243041",
        accent: "#4fd1c5",
      },
    },
  },
  plugins: [],
};

export default config;

