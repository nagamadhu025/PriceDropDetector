// DarkModeToggle.jsx

import { useEffect, useState } from "react";
import "./darkmode.css";

function DarkModeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check saved preference
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
      setIsDark(true);
      document.body.classList.add("dark-mode");
    }
  }, []);

  const toggleDarkMode = () => {
    setIsDark(!isDark);
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("theme", !isDark ? "dark" : "light");
  };

  return (
    <button
      className="dark-mode-toggle"
      onClick={toggleDarkMode}
      title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
    >
      {isDark ? "☀️" : "🌙"}
    </button>
  );
}

export default DarkModeToggle;