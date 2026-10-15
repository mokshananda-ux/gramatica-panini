import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        parchment: {
          50: "#fdfbf7",
          100: "#f9f4eb",
          200: "#f0e6d3",
          300: "#e4d4b5",
        },
        ink: {
          700: "#2c2416",
          800: "#1a1510",
          900: "#0f0c08",
        },
        saffron: {
          400: "#e8a838",
          500: "#d4922a",
          600: "#b87a1f",
        },
        terracotta: {
          500: "#c45c3e",
          600: "#a84a30",
        },
      },
      fontFamily: {
        serif: ["var(--font-literata)", "Georgia", "serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "Cascadia Code", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
