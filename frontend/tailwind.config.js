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
          50: '#f2f8f5',
          100: '#e2f0e8',
          200: '#c4e2d2',
          300: '#99cbb2',
          400: '#68ae8a',
          500: '#40916c', // Main green
          600: '#2d6a4f', // Deep nature green
          700: '#21503b',
          800: '#1b3f2f',
          900: '#153125',
          950: '#0c1b14',
        },
        secondary: {
          50: '#fdfbf7',
          100: '#faedcd', // Warm clay light
          200: '#ccd5ae', // Moss light
          300: '#d4a373', // Warm sand/earth
          400: '#bfa07a',
          500: '#aa825c',
          600: '#8c6543',
          700: '#6c4a30',
        },
        accent: {
          50: '#f0f9fb',
          100: '#e0f3f7',
          500: '#219ebc', // Tech/AI blue
          600: '#028090',
        },
        darkbg: {
          50: '#2c2c30',  // Deep charcoal card
          100: '#1b1b1e', // Dark mode background
          200: '#141416',
        },
        status: {
          success: '#2d6a4f',
          warning: '#f4a261',
          danger: '#e76f51',
          info: '#219ebc',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'sans-serif'],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.08)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.08)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
      }
    },
  },
  plugins: [],
}
