/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gem: {
          blue: "#0A2540",
          navy: "#0F172A",
          gold: "#D97706",
          accent: "#2563EB",
          light: "#F8FAFC"
        }
      }
    },
  },
  plugins: [],
}
