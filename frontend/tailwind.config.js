/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f2f9f1',
          100: '#e1f0de',
          200: '#c5e2be',
          300: '#9dcd92',
          400: '#6eb162',
          500: '#4e9742',
          600: '#3c7c31',
          700: '#326229',
          800: '#2b4f24',
          900: '#24421f',
          950: '#10240e',
        },
        darkbg: {
          50: '#181e1b',
          100: '#0f1412',
        }
      }
    },
  },
  plugins: [],
}
