/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        panel: "#0b1220",
        accent: "#4f46e5",
        cyanGlow: "#06b6d4"
      },
      boxShadow: {
        scientific: "0 25px 60px rgba(15, 23, 42, 0.22)"
      },
      keyframes: {
        floatin: {
          "0%": { opacity: 0, transform: "translateY(18px)" },
          "100%": { opacity: 1, transform: "translateY(0)" }
        }
      },
      animation: {
        floatin: "floatin 500ms ease forwards"
      }
    }
  },
  plugins: [],
};

