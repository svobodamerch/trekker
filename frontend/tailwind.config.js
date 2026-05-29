/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        soft: {
          50: '#f6f7f9',
          100: '#eceef2',
          200: '#d5dae2',
          300: '#b3bcc9',
          400: '#8a97ab',
          500: '#6b7b94',
          600: '#56637a',
          700: '#475163',
          800: '#3d4554',
          900: '#363c48',
        },
      },
    },
  },
  plugins: [],
}
