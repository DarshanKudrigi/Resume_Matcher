# ResumeMate 📄

An intuitive, client-side application that matches resumes against job descriptions, analyzes skill gaps, checks ATS compatibility, provides the learning resources and interactive resume builder with AI suggestions.

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## ✨ Features

- 🎯 **AI Match Scoring:** Instant percentage match calculation between your resume and target job descriptions.
- 🔍 **Skill Gap Analysis:** Categorized breakdown showing matched, partial, and missing technical skills.
- 📋 **ATS Checker:** Analyzes section headers, contact info integrity, layout parsability, and keyword density.
- 📚 **Learning resources:** Recommended study paths and curated free learning resources for missing skills.
- 🤖 **AI Assistant:** Built-in interactive chatbot to answer questions about your score, gaps, and resume improvements.
- 📝 **Live Resume Builder:** Interactive dual-pane editor with live preview, 3 ATS-friendly templates (*Modern*, *Classic*, *Minimal*), AI writing suggestions, and one-click **PDF Export**.


---

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite 8, React Router 7
- **Styling:** Tailwind CSS, Custom Warm Editorial Palette
- **Icons:** Lucide React
- **Linter:** Oxlint

---

## 🚀 Quick Start

### 1. Prerequisites
Make sure you have **Node.js** (v18+) and **npm** installed.

### 2. Installation & Running

```bash
# Clone the repository
git clone https://github.com/your-username/resume-matcher.git

# Navigate into the project directory
cd "resume matcher"

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open `http://localhost:5173` in your browser to view the app.

---

## 📁 Project Structure

```plaintext
src/
├── components/     # Reusable UI components (ATSChecker, ChatBox, ResumeForm, etc.)
├── context/        # AppContext & ThemeContext for global state
├── data/           # Mock sample job postings, profile data, and AI suggestions
├── pages/          # Application views (Dashboard, Analyzer, Results, Builder, etc.)
├── App.jsx         # Routes & app wrapper
├── main.jsx        # App entry point
└── index.css       # Tailwind directives & theme styles
```

---

## 📜 Available Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev` | Runs the development server at `localhost:5173` |
| `npm run build` | Builds the project for production |
| `npm run preview` | Previews the production build locally |
| `npm run lint` | Lints the codebase using Oxlint |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
hello this is from darshan repo.
