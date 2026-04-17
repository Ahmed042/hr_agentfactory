/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#1E3A8A',
          600: '#1E3A8A',
          700: '#1E3A8A',
          DEFAULT: '#1E3A8A',
        },
        navy: {
          50: '#F0F4FF',
          100: '#E0E8FF',
          500: '#1E3A8A',
          600: '#1B3578',
          700: '#172E66',
          800: '#132654',
          900: '#0F1E42',
        },
        secondary: '#64748B',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
