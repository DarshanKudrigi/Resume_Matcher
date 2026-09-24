/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        warm: {
          bg: '#F7F5F0',
          card: '#FFFFFF',
          primary: '#7C5C3B',
          'primary-hover': '#66492C',
          secondary: '#A67C52',
          'secondary-hover': '#8F6840',
          accent: '#D8A48F',
          text: '#2F2A26',
          muted: '#77716B',
          border: '#E7E0D8',
          success: '#6B8E6B',
          warning: '#C99545',
          error: '#B96A63',
          dark: {
            bg: '#1F1D1A',
            card: '#292622',
            primary: '#C49A6C',
            'primary-hover': '#B38757',
            secondary: '#D8B08A',
            text: '#F4EFE8',
            muted: '#B9B0A5',
            border: '#413B34',
          }
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'warm-sm': '0 1px 2px 0 rgba(47, 42, 38, 0.05)',
        'warm': '0 4px 12px 0 rgba(47, 42, 38, 0.07)',
        'warm-md': '0 6px 16px -2px rgba(47, 42, 38, 0.08)',
        'warm-lg': '0 12px 28px -4px rgba(47, 42, 38, 0.12)',
        'warm-dark-sm': '0 1px 3px 0 rgba(0, 0, 0, 0.25)',
        'warm-dark-md': '0 6px 16px -2px rgba(0, 0, 0, 0.35)',
      }
    },
  },
  plugins: [],
}
