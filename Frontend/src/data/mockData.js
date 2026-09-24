// src/data/mockData.js
// Centralized mock data layer for ResumeMate


export const initialUser = {
  name: "Darshan Sharma",
  email: "darshan.sharma@college.edu",
  phone: "+91 98765 43210",
  location: "Mumbai, India",
  headline: "Aspiring Frontend Engineer & CS Undergraduate",
  avatar: "DS",
  linkedin: "linkedin.com/in/darshansharma",
  github: "github.com/darshan-cs",
  portfolio: "darshansharma.dev",
  college: "National Institute of Technology",
  degree: "B.Tech in Computer Science and Engineering",
  graduationYear: "2026",
  notifications: [
    { id: 1, title: "Analysis Complete", message: "Your resume match score for Apex Cloud is 82%.", time: "10m ago", unread: true },
    { id: 2, title: "ATS Tip", message: "Adding 'Docker' can increase your score by up to 8%.", time: "2h ago", unread: true },
    { id: 3, title: "Resume Saved", message: "Frontend Developer Resume was updated.", time: "1d ago", unread: false },
  ]
};

export const sampleJobPostings = [
  {
    id: "job-1",
    title: "Frontend Software Engineer (React)",
    company: "Apex Cloud Technologies",
    location: "Bengaluru, India (Hybrid)",
    url: "https://careers.apexcloud.io/jobs/frontend-engineer-react",
    posted: "3 days ago",
    experience: "0-2 Years",
    description: `We are looking for a passionate Frontend Software Engineer with a solid foundation in modern JavaScript, React, HTML, and CSS to join our core product team.

Responsibilities:
- Build responsive, accessible, and high-performance user interfaces using React and modern CSS.
- Collaborate with product designers and backend engineers to integrate RESTful APIs.
- Write modular, clean, and reusable component code using Git for version control.
- Participate in code reviews and contribute to developer documentation.

Requirements:
- Strong proficiency in JavaScript (ES6+), React hooks, HTML5, and CSS3.
- Hands-on experience with Git version control and collaborative workflows.
- Understanding of web performance, responsive layouts, and cross-browser quirks.
- Preferred familiarity with Node.js, Docker containers, and AWS cloud deployment environments.`,
    requiredSkills: ["JavaScript", "React", "HTML", "CSS", "Git"],
    preferredSkills: ["Node.js", "Docker", "AWS"]
  },
  {
    id: "job-2",
    title: "Junior Full Stack Developer",
    company: "FinTech Innovations",
    location: "Pune, India (Remote)",
    url: "https://fintechinnovations.com/careers/junior-dev",
    posted: "5 days ago",
    experience: "Entry Level / College Grad",
    description: `Join our agile engineering squad developing next-generation financial analytics tools.
Seeking candidates with React, TypeScript/JavaScript, Node.js, and SQL fundamentals. Knowledge of Docker, REST APIs, and automated testing is highly valued.`,
    requiredSkills: ["JavaScript", "React", "Node.js", "SQL", "Git"],
    preferredSkills: ["Docker", "TypeScript", "REST APIs", "Jest"]
  }
];

export const initialAnalysisResult = {
  jobTitle: "Frontend Software Engineer (React)",
  company: "Apex Cloud Technologies",
  matchScore: 82,
  atsScore: 86,
  status: "Strong Match",
  summary: "Your profile exhibits exceptional alignment with core frontend engineering competencies, notably in modern JavaScript, React ecosystem, and responsive layout development. Addressing secondary gaps in Docker containerization and foundational AWS cloud workflows will make your application stand out significantly.",
  matchedSkills: ["JavaScript", "React", "HTML", "CSS", "Git"],
  missingSkills: ["Docker", "AWS", "System Design"],
  partialSkills: ["Node.js"],
  skillGaps: [
    { skill: "JavaScript", status: "Strong", score: 95, category: "Core Frontend", description: "Demonstrated through modern ES6+ projects, async programming, and state management." },
    { skill: "React", status: "Strong", score: 92, category: "Core Frontend", description: "Extensive functional components, custom hooks, and React Router navigation." },
    { skill: "HTML", status: "Strong", score: 90, category: "Core Frontend", description: "Semantic markup, accessible landmarks, and modern web standards." },
    { skill: "CSS", status: "Strong", score: 88, category: "Core Frontend", description: "Tailwind CSS, flexbox, grid, and adaptive responsive mobile design." },
    { skill: "Git", status: "Strong", score: 85, category: "Version Control", description: "Branching strategies, pull request workflows, and merge conflict resolution." },
    { skill: "Node.js", status: "Good", score: 65, category: "Backend / APIs", description: "Basic REST endpoint creation and Express server integration; could showcase more middleware patterns." },
    { skill: "Docker", status: "Missing", score: 20, category: "DevOps & Deployment", description: "No explicit containerization or Dockerfile construction identified in your uploaded resume." },
    { skill: "AWS", status: "Missing", score: 15, category: "Cloud Infrastructure", description: "Missing cloud hosting (S3, CloudFront, EC2) or deployment pipeline references." },
    { skill: "System Design", status: "Missing", score: 25, category: "Architecture", description: "High-level caching, CDN edge delivery, and frontend architecture not emphasized." }
  ],
  learningRecommendations: [
    {
      id: "rec-docker",
      skill: "Docker",
      subtitle: "Learn containerization and deployment basics.",
      difficulty: "Beginner to Intermediate",
      estimatedTime: "6–8 Hours",
      summary: "Understand container concepts, craft multi-stage Dockerfiles for React single-page apps, and configure local container stacks.",
      keyTopics: ["Dockerfiles & Layers", "Containerizing React Vite Apps", "Nginx Static Serving", "Docker Compose"],
      resources: [
        { title: "Docker for Frontend Developers", type: "Interactive Video", provider: "freeCodeCamp", duration: "2.5 Hours", link: "#" },
        { title: "Containerize a React App with Nginx", type: "Official Walkthrough", provider: "Docker Documentation", duration: "45 Mins", link: "#" },
        { title: "Docker Compose for Local Web Stacks", type: "Hands-on Guide", provider: "Web Dev Community", duration: "1.5 Hours", link: "#" }
      ]
    },
    {
      id: "rec-aws",
      skill: "AWS",
      subtitle: "Learn core cloud services and deployment.",
      difficulty: "Intermediate",
      estimatedTime: "10–12 Hours",
      summary: "Master deploying web applications to Amazon S3, configuring CloudFront CDN for global caching, and securing routes with IAM.",
      keyTopics: ["Amazon S3 Static Hosting", "CloudFront CDN Caching", "Route 53 Custom Domains", "AWS IAM Security Essentials"],
      resources: [
        { title: "AWS Cloud Practitioner Essentials", type: "Free Course", provider: "AWS Skill Builder", duration: "6 Hours", link: "#" },
        { title: "Deploying Modern React SPAs to S3 + CloudFront", type: "Tutorial", provider: "AWS Community", duration: "1.5 Hours", link: "#" },
        { title: "AWS Lambda & Serverless for Frontends", type: "Practical Lab", provider: "Cloud Guru Labs", duration: "2 Hours", link: "#" }
      ]
    },
    {
      id: "rec-sysdesign",
      skill: "System Design",
      subtitle: "Learn scalability, APIs and architecture fundamentals.",
      difficulty: "Intermediate to Advanced",
      estimatedTime: "8–10 Hours",
      summary: "Understand client-side state architecture, bundle splitting, CDN caching, rate limiting, and scalable REST API conventions.",
      keyTopics: ["Frontend Performance & Core Web Vitals", "Client-Side Caching (SWR/React Query)", "Code Splitting & Lazy Loading", "RESTful API Conventions & Error Handling"],
      resources: [
        { title: "Frontend System Design Handbook", type: "Open Source Guide", provider: "GitHub / GreatFrontEnd", duration: "4 Hours", link: "#" },
        { title: "Optimizing Web Vitals for Production", type: "Engineering Guide", provider: "web.dev by Google", duration: "2 Hours", link: "#" },
        { title: "Designing Resilient API Clients", type: "Deep Dive Article", provider: "Engineering Blog", duration: "1.5 Hours", link: "#" }
      ]
    }
  ],
  atsBreakdown: {
    score: 86,
    verdict: "ATS Passed with Minor Keyword Enhancements",
    items: [
      { id: "contact", label: "Contact Information", passed: true, note: "Full name, phone, email, GitHub, and LinkedIn verified." },
      { id: "skills", label: "Skills Section", passed: true, note: "Categorized skills list found with industry-standard naming." },
      { id: "education", label: "Education & Credentials", passed: true, note: "Accredited university degree and graduation year parsed." },
      { id: "projects", label: "Project Descriptions", passed: true, note: "Impact statements and technical stacks are prominently visible." },
      { id: "keywords", label: "Job-Specific Keywords", passed: false, note: "Warning: Add keywords like 'Docker', 'AWS', and 'CI/CD'." },
      { id: "layout", label: "Clean ATS Layout", passed: true, note: "Standard single/two-column format without unreadable tables." }
    ]
  }
};

export const defaultResumeData = {
  id: "resume-1",
  title: "Frontend Developer Resume",
  template: "modern", // 'classic' | 'modern' | 'minimal'
  updatedAt: "Today",
  atsScore: 86,
  personalInfo: {
    fullName: "Darshan Sharma",
    email: "darshan.sharma@college.edu",
    phone: "+91 98765 43210",
    location: "Mumbai, India",
    linkedin: "linkedin.com/in/darshansharma",
    github: "github.com/darshan-cs",
    portfolio: "darshansharma.dev",
    headline: "Frontend React Developer & Final Year CS Student"
  },
  summary: "Driven Computer Science undergraduate with practical experience in crafting responsive, user-centric web applications using React, JavaScript (ES6+), and modern CSS frameworks. Adept at building modular component architectures, optimizing client-side performance, and collaborating via Git version control.",
  education: [
    {
      id: "edu-1",
      institution: "National Institute of Technology",
      degree: "B.Tech in Computer Science & Engineering",
      location: "Mumbai, India",
      startDate: "Aug 2022",
      endDate: "Expected May 2026",
      score: "CGPA: 8.8 / 10.0"
    },
    {
      id: "edu-2",
      institution: "Delhi Public School",
      degree: "Higher Secondary Education (PCM)",
      location: "Mumbai, India",
      startDate: "2020",
      endDate: "2022",
      score: "Percentage: 94.2%"
    }
  ],
  experience: [
    {
      id: "exp-1",
      role: "Frontend Engineering Intern",
      company: "InnovateTech Solutions",
      location: "Remote",
      startDate: "May 2025",
      endDate: "Jul 2025",
      bullets: [
        "Engineered 12+ responsive React components for customer analytics dashboard, reducing render times by 22%.",
        "Integrated REST APIs with stateful custom hooks and implemented client-side form validation.",
        "Collaborated with senior engineers in bi-weekly Agile sprints, participating in Git code reviews."
      ]
    }
  ],
  projects: [
    {
      id: "proj-1",
      name: "ResumeMate - AI Resume & Job Matcher",
      tech: "React, Tailwind CSS, JavaScript, Context API",
      link: "https://github.com/darshan-cs/resume-mate",
      bullets: [
        "Developed a modern client-side matching tool analyzing resumes against job descriptions with visual skill gap indicators.",
        "Constructed an interactive live-preview resume builder supporting multiple modular themes and ATS compatibility evaluation.",
        "Built responsive interfaces adhering to strict accessibility guidelines and light/dark theme persistence."
      ]
    },
    {
      id: "proj-2",
      name: "CampusConnect - Student Collab Portal",
      tech: "React, Node.js, Express, MongoDB",
      link: "https://github.com/darshan-cs/campus-connect",
      bullets: [
        "Created peer-to-peer project discovery platform adopted by 400+ students across campus.",
        "Implemented secure JWT authentication, real-time comment threads, and file sharing."
      ]
    }
  ],
  skills: {
    languages: ["JavaScript (ES6+)", "HTML5", "CSS3/Tailwind", "Python (Basics)", "SQL"],
    frameworks: ["React.js", "React Router", "Vite", "Node.js (Express Basics)"],
    tools: ["Git", "GitHub", "VS Code", "Postman", "Figma (Inspect)"],
    concepts: ["Component Architecture", "RESTful APIs", "Responsive Web Design", "Data Structures"]
  },
  certifications: [
    {
      id: "cert-1",
      name: "Meta Front-End Developer Professional Certificate",
      issuer: "Coursera",
      year: "2025"
    },
    {
      id: "cert-2",
      name: "JavaScript Algorithms and Data Structures",
      issuer: "freeCodeCamp",
      year: "2024"
    }
  ],
  achievements: [
    {
      id: "ach-1",
      title: "1st Runner-Up, Inter-College Hackathon 2025",
      detail: "Built an accessibility-focused browser extension among 60+ participating teams."
    },
    {
      id: "ach-2",
      title: "Dean's Academic Honor Roll",
      detail: "Awarded top 5% academic standing in School of Computer Engineering for 2024-2025."
    }
  ]
};

export const initialSavedResumes = [
  {
    ...defaultResumeData,
    id: "res-1",
    title: "Frontend Developer Resume",
    atsScore: 86,
    updatedAt: "Today",
    targetRole: "Frontend Software Engineer",
    tags: ["React", "JavaScript", "Tailwind CSS"]
  },
  {
    ...defaultResumeData,
    id: "res-2",
    title: "Software Engineer Resume",
    atsScore: 82,
    updatedAt: "2 days ago",
    targetRole: "Full Stack Engineer",
    tags: ["React", "Node.js", "SQL", "Git"]
  },
  {
    ...defaultResumeData,
    id: "res-3",
    title: "Full Stack Intern Resume",
    atsScore: 79,
    updatedAt: "1 week ago",
    targetRole: "Software Engineering Intern",
    tags: ["JavaScript", "Python", "Web Development"]
  }
];

export const initialHistory = [
  {
    id: "hist-1",
    jobTitle: "Frontend Developer",
    company: "Apex Cloud Technologies",
    matchScore: 82,
    atsScore: 86,
    date: "Today, 11:20 AM",
    dateFormatted: "Today",
    status: "Strong Match",
    missingCount: 3,
    matchedCount: 5,
    skills: ["JavaScript", "React", "HTML", "CSS", "Git"]
  },
  {
    id: "hist-2",
    jobTitle: "Software Engineer",
    company: "FinTech Global",
    matchScore: 76,
    atsScore: 80,
    date: "Sep 18, 2026",
    dateFormatted: "Sep 18",
    status: "Good Match",
    missingCount: 4,
    matchedCount: 6,
    skills: ["React", "JavaScript", "SQL", "Node.js"]
  },
  {
    id: "hist-3",
    jobTitle: "Data Analyst",
    company: "DataScale AI",
    matchScore: 71,
    atsScore: 74,
    date: "Sep 15, 2026",
    dateFormatted: "Sep 15",
    status: "Moderate Match",
    missingCount: 5,
    matchedCount: 4,
    skills: ["Python", "SQL", "Git"]
  },
  {
    id: "hist-4",
    jobTitle: "React Developer Intern",
    company: "NextGen Labs",
    matchScore: 88,
    atsScore: 91,
    date: "Aug 29, 2026",
    dateFormatted: "Aug 29",
    status: "Excellent Match",
    missingCount: 2,
    matchedCount: 7,
    skills: ["React", "JavaScript", "HTML", "CSS", "Git", "REST APIs"]
  }
];

export const chatResponses = [
  {
    triggers: ["why is my match score 82%", "82%", "match score", "why 82"],
    question: "Why is my match score 82%?",
    response: "Your 82% match score is calculated because you satisfy 100% of the core required skills (JavaScript, React, HTML, CSS, and Git) and partially cover Node.js. However, the job description also prefers Docker, AWS, and System Design, which are currently not detected in your resume."
  },
  {
    triggers: ["what skills am i missing", "missing skills", "skills missing", "what am i missing"],
    question: "What skills am I missing?",
    response: "Based on the Apex Cloud job requirements, your primary missing skills are:\n1. Docker (containerization)\n2. AWS (cloud deployment and hosting)\n3. System Design (scalability & performance fundamentals)\n\nAdditionally, Node.js is considered a partial match."
  },
  {
    triggers: ["how can i improve my resume", "improve resume", "tips to improve", "improve"],
    question: "How can I improve my resume?",
    response: "Here are 3 high-impact ways to improve:\n• Add quantifiable bullet points (e.g., 'reduced render time by 22%').\n• Include a small Dockerized project to check off containerization requirements.\n• Mention basic AWS deployment (like hosting your React app on S3 + CloudFront).\n• Ensure standard ATS section headers are maintained."
  },
  {
    triggers: ["what should i learn first", "learn first", "learning order", "where to start"],
    question: "What should I learn first?",
    response: "We recommend starting with Docker (estimated 6-8 hours). It has the fastest learning curve for a frontend engineer and immediately fulfills a preferred qualification. Following that, explore AWS S3/CloudFront hosting before diving into System Design."
  },
  {
    triggers: ["ats", "ats score", "ats check", "compatibility"],
    question: "How does the ATS score work?",
    response: "The ATS (Applicant Tracking System) check verifies formatting readability, keyword presence, contact details, and clean section headers. Your current ATS score is 86%. Adding target keywords like 'Docker' and 'AWS' will raise it further."
  }
];

export const aiSuggestions = {
  summaries: [
    "Performance-focused Frontend Engineer with expertise in building responsive React SPAs, component libraries, and RESTful API integrations. Passionate about clean code, accessibility, and modern developer tooling.",
    "Driven CS undergraduate with hands-on experience developing intuitive frontend interfaces using React, JavaScript (ES6+), and Tailwind CSS. Proven ability to translate UX mockups into pixel-perfect web applications.",
    "Detail-oriented software developer specializing in modern React ecosystems, state management, and Git workflows. Proven track record in collaborative hackathons and production-ready academic web tools."
  ],
  bulletPoints: [
    "Architected reusable React components with custom hooks, reducing code redundancy across pages by 35%.",
    "Optimized asset loading and implemented code splitting, improving Core Web Vitals and First Contentful Paint by 40%.",
    "Implemented client-side caching and debounced search, cutting redundant network requests by 50%.",
    "Integrated responsive mobile-first layouts using Tailwind CSS, ensuring seamless cross-device compatibility."
  ],
  projectDescriptions: [
    "Engineered a high-performance web dashboard featuring dynamic filtering, responsive grid layouts, and seamless local persistence using modern React hooks.",
    "Developed an end-to-end full-stack prototype with clean modular architecture, comprehensive error handling, and robust form validation.",
    "Designed and shipped a responsive single-page web app with 95+ Lighthouse accessibility and performance ratings."
  ]
};
