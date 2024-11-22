/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*"],
  darkMode: "class",
  theme: {
    screens: {
      sm: "480px",
      md: "768px",
      lg: "976px",
      xl: "1400px",
    },
    extend: {
      colors: {
        
        whiteColor: "#fff",
        textColor: "#DDD",
        secondaryColor: "#B7E4C7"
      },
      keyframes: {
        move: {
          "50%": { transform: "scale(1.1)" }
        }
      },
      animation: {
        scaleAnimation: "move 3s linear infinite"
      }
    },
    container: {
      center: true,
      padding: {
        DEFAULT: "10px",
        md: "30px",
      },
    },
    fontFamily: {
      poppins: ["Poppins", "sans-serif"],
      Londrina: ["Londrina Outline", "sans-serif"],
    },
  },
  plugins: [],
}