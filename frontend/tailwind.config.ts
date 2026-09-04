import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F5F6F2",
        ink: "#171B24",
        navy: {
          DEFAULT: "#1B2A4A",
          light: "#2F4270",
          dark: "#101A30",
        },
        signal: {
          DEFAULT: "#E0932F",
          soft: "#F3D9AE",
        },
        match: {
          DEFAULT: "#3F6B52",
          soft: "#D8E6DC",
        },
        gap: {
          DEFAULT: "#B4472B",
          soft: "#F0DAD3",
        },
        line: "#DEDBD1",
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "serif"],
        body: ["var(--font-plex)", "sans-serif"],
      },
      maxWidth: {
        prose: "68ch",
      },
    },
  },
  plugins: [],
};

export default config;
