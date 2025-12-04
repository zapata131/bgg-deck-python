/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#8367C7',
          foreground: '#FFFFFF',
        },
        background: '#F5F0E9',
        foreground: '#3A3A3A',
        card: '#FFFFFF',
        muted: '#F5F0E9',
        'muted-foreground': '#6B6B6B',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.625rem',
      },
    },
  },
  plugins: [],
}
