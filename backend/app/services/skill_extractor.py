import re
import logging
from typing import Dict, List, Set, Tuple, Optional

logger = logging.getLogger("resumemate.nlp")

# Lazy spaCy loader
_spacy_nlp = None

def get_spacy_nlp():
    """Lazily loads the spaCy model if installed, otherwise returns None."""
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy en_core_web_sm model loaded successfully.")
        except Exception:
            _spacy_nlp = False
    return _spacy_nlp if _spacy_nlp is not False else None


# Comprehensive taxonomy: canonical_name -> {category, aliases, description}
SKILLS_TAXONOMY: Dict[str, Dict] = {
    # Core Languages
    "Python": {
        "category": "Programming Languages",
        "aliases": ["python", "python3", "py"],
        "description": "Backend services, scripting, automation, and algorithmic data structures."
    },
    "JavaScript": {
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "es6", "es6+", "ecmascript"],
        "description": "Demonstrated through modern ES6+ projects, async programming, and state management."
    },
    "TypeScript": {
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"],
        "description": "Strict type safety, generic interfaces, and enterprise frontend architecture."
    },
    "Java": {
        "category": "Programming Languages",
        "aliases": ["java", "jvm"],
        "description": "Object-oriented software development, enterprise microservices, and design patterns."
    },
    "C++": {
        "category": "Programming Languages",
        "aliases": ["c++", "cpp"],
        "description": "High-performance systems programming, memory management, and competitive programming."
    },
    "C": {
        "category": "Programming Languages",
        "aliases": ["c language", "c programming", "ansi c"],
        "description": "Low-level systems programming, pointers, and memory manipulation."
    },
    "C#": {
        "category": "Programming Languages",
        "aliases": ["c#", "csharp", "c-sharp", ".net c#"],
        "description": "Object-oriented development on the .NET ecosystem."
    },
    "Go": {
        "category": "Programming Languages",
        "aliases": ["golang", "go language"],
        "description": "Concurrent goroutines, microservice architectures, and high-throughput network services."
    },
    "Rust": {
        "category": "Programming Languages",
        "aliases": ["rust", "rustlang"],
        "description": "Memory-safe systems programming, concurrency, and WebAssembly."
    },
    "PHP": {
        "category": "Programming Languages",
        "aliases": ["php", "php8"],
        "description": "Server-side web scripting and legacy application maintenance."
    },
    "Ruby": {
        "category": "Programming Languages",
        "aliases": ["ruby", "ruby on rails", "rails"],
        "description": "Rapid application development and elegant object-oriented code."
    },
    "Swift": {
        "category": "Programming Languages",
        "aliases": ["swift", "swiftui"],
        "description": "Native iOS, iPadOS, and macOS software development."
    },
    "Kotlin": {
        "category": "Programming Languages",
        "aliases": ["kotlin", "android kotlin"],
        "description": "Modern Android app development and coroutine-based async workflows."
    },
    "SQL": {
        "category": "Databases & Storage",
        "aliases": ["sql", "relational database", "rdbms", "sql queries"],
        "description": "Relational querying, joins, aggregations, indexing, and normalization."
    },
    "HTML": {
        "category": "Core Frontend",
        "aliases": ["html", "html5", "semantic html"],
        "description": "Semantic markup, accessible landmarks, and modern web standards."
    },
    "CSS": {
        "category": "Core Frontend",
        "aliases": ["css", "css3", "flexbox", "grid", "responsive design"],
        "description": "Tailwind CSS, Flexbox, CSS Grid, and adaptive responsive mobile design."
    },

    # Core Frontend Frameworks & UI
    "React": {
        "category": "Core Frontend",
        "aliases": ["react", "react.js", "reactjs", "react hooks"],
        "description": "Functional components, custom hooks, virtual DOM, and component lifecycles."
    },
    "Next.js": {
        "category": "Core Frontend",
        "aliases": ["next.js", "nextjs", "next 14", "next 15", "app router"],
        "description": "Server-side rendering (SSR), static site generation (SSG), and edge routing."
    },
    "Vue.js": {
        "category": "Core Frontend",
        "aliases": ["vue", "vue.js", "vuejs", "vue 3", "pinia"],
        "description": "Composition API, reactive state management, and Vue Router."
    },
    "Angular": {
        "category": "Core Frontend",
        "aliases": ["angular", "angularjs", "ng"],
        "description": "Dependency injection, RxJS streams, and enterprise component architecture."
    },
    "Tailwind CSS": {
        "category": "Core Frontend",
        "aliases": ["tailwind", "tailwindcss", "tailwind-css"],
        "description": "Utility-first modern styling, responsive variants, and dark theme support."
    },
    "Redux": {
        "category": "Core Frontend",
        "aliases": ["redux", "redux toolkit", "rtk"],
        "description": "Global predictable state container, selectors, and async middleware."
    },
    "Bootstrap": {
        "category": "Core Frontend",
        "aliases": ["bootstrap", "bootstrap 5"],
        "description": "Responsive grid layout, UI components, and mobile-first design."
    },

    # Backend / APIs
    "Node.js": {
        "category": "Backend / APIs",
        "aliases": ["node", "node.js", "nodejs"],
        "description": "REST endpoint creation, Express server integration, and event loop handling."
    },
    "FastAPI": {
        "category": "Backend / APIs",
        "aliases": ["fastapi", "fast-api"],
        "description": "Asynchronous RESTful APIs, OpenAPI docs, and Pydantic validation."
    },
    "Express": {
        "category": "Backend / APIs",
        "aliases": ["express", "express.js", "expressjs"],
        "description": "Middleware routing, server request pipelines, and REST handlers."
    },
    "Django": {
        "category": "Backend / APIs",
        "aliases": ["django", "django rest framework", "drf"],
        "description": "Batteries-included web framework, ORM models, and secure authentication."
    },
    "Flask": {
        "category": "Backend / APIs",
        "aliases": ["flask", "flask-restful"],
        "description": "Microframework for Python APIs and lightweight backend services."
    },
    "Spring Boot": {
        "category": "Backend / APIs",
        "aliases": ["spring boot", "spring framework", "spring"],
        "description": "Enterprise Java microservices, dependency injection, and REST controllers."
    },
    "GraphQL": {
        "category": "Backend / APIs",
        "aliases": ["graphql", "apollo client", "apollo server"],
        "description": "Schema definition, queries, mutations, and client cache normalization."
    },
    "REST APIs": {
        "category": "Backend / APIs",
        "aliases": ["rest", "rest api", "rest apis", "restful", "restful apis"],
        "description": "HTTP method semantics, resource-based design, and JSON payload handling."
    },

    # Databases & Storage
    "PostgreSQL": {
        "category": "Databases & Storage",
        "aliases": ["postgres", "postgresql", "psql"],
        "description": "ACID compliance, JSONB queries, connection pooling, and relational schemas."
    },
    "MySQL": {
        "category": "Databases & Storage",
        "aliases": ["mysql", "mariadb"],
        "description": "Relational storage, index optimization, and transaction handling."
    },
    "MongoDB": {
        "category": "Databases & Storage",
        "aliases": ["mongodb", "mongo", "nosql"],
        "description": "Document-based schemas, aggregation pipelines, and flexible JSON records."
    },
    "Redis": {
        "category": "Databases & Storage",
        "aliases": ["redis", "in-memory cache"],
        "description": "In-memory key-value caching, session stores, and pub/sub messaging."
    },
    "SQLite": {
        "category": "Databases & Storage",
        "aliases": ["sqlite", "sqlite3"],
        "description": "Embedded relational database engine for client and development environments."
    },

    # Cloud & DevOps
    "Docker": {
        "category": "DevOps & Deployment",
        "aliases": ["docker", "container", "containers", "dockerfile", "containerization"],
        "description": "Container concepts, crafting multi-stage Dockerfiles, and container orchestration."
    },
    "Kubernetes": {
        "category": "DevOps & Deployment",
        "aliases": ["kubernetes", "k8s"],
        "description": "Pod scheduling, service discovery, ingress controllers, and auto-scaling."
    },
    "AWS": {
        "category": "Cloud Infrastructure",
        "aliases": ["aws", "amazon web services", "s3", "ec2", "cloudfront", "lambda"],
        "description": "Cloud hosting (S3, CloudFront, EC2) and deployment pipeline references."
    },
    "Azure": {
        "category": "Cloud Infrastructure",
        "aliases": ["azure", "microsoft azure"],
        "description": "Microsoft cloud computing services and application hosting."
    },
    "Google Cloud": {
        "category": "Cloud Infrastructure",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
        "description": "Google Cloud infrastructure, compute engine, and cloud storage."
    },
    "CI/CD": {
        "category": "DevOps & Deployment",
        "aliases": ["ci/cd", "ci cd", "github actions", "gitlab ci", "jenkins"],
        "description": "Automated build, test, and continuous delivery pipelines."
    },
    "Git": {
        "category": "Version Control",
        "aliases": ["git", "github", "gitlab", "version control"],
        "description": "Branching strategies, pull request workflows, and merge conflict resolution."
    },
    "Linux": {
        "category": "DevOps & Deployment",
        "aliases": ["linux", "ubuntu", "bash", "unix", "shell scripting"],
        "description": "Command-line navigation, file permissions, and server administration."
    },

    # AI, Machine Learning & Data
    "Machine Learning": {
        "category": "AI & Data Science",
        "aliases": ["machine learning", "ml", "deep learning", "neural networks"],
        "description": "Supervised, unsupervised algorithms, model evaluation, and training pipelines."
    },
    "PyTorch": {
        "category": "AI & Data Science",
        "aliases": ["pytorch", "torch"],
        "description": "Deep learning tensor operations, neural network layers, and GPU training."
    },
    "TensorFlow": {
        "category": "AI & Data Science",
        "aliases": ["tensorflow", "keras"],
        "description": "Machine learning graph modeling and enterprise model deployment."
    },
    "NLP": {
        "category": "AI & Data Science",
        "aliases": ["nlp", "natural language processing", "text mining"],
        "description": "Text tokenization, sentiment analysis, NER, and language models."
    },
    "spaCy": {
        "category": "AI & Data Science",
        "aliases": ["spacy"],
        "description": "Industrial-strength natural language processing library for Python."
    },
    "Pandas": {
        "category": "AI & Data Science",
        "aliases": ["pandas"],
        "description": "Data analysis, DataFrame manipulation, filtering, and time series."
    },
    "NumPy": {
        "category": "AI & Data Science",
        "aliases": ["numpy"],
        "description": "Numerical multi-dimensional arrays, matrix math, and vectorized computing."
    },

    # Architecture & Testing
    "System Design": {
        "category": "Architecture",
        "aliases": ["system design", "distributed systems", "scalability", "architecture", "microservices"],
        "description": "High-level caching, CDN edge delivery, rate limiting, and backend architecture."
    },
    "Data Structures": {
        "category": "Foundations",
        "aliases": ["data structures", "algorithms", "dsa"],
        "description": "Arrays, trees, graphs, hashing, and asymptotic algorithmic complexity."
    },
    "Testing": {
        "category": "Quality Assurance",
        "aliases": ["jest", "cypress", "playwright", "vitest", "unit test", "unit testing", "pytest"],
        "description": "Unit testing, end-to-end user flows, test assertions, and mock coverage."
    },
    "Agile": {
        "category": "Methodologies",
        "aliases": ["agile", "scrum", "sprint", "kanban", "jira"],
        "description": "Iterative sprint delivery, standups, and cross-functional collaboration."
    }
}

def extract_skills_from_text(text: str) -> List[str]:
    """Scans text and returns canonical skill names present in the content."""
    if not text:
        return []
    
    found_skills: Set[str] = set()
    lower_text = " " + text.lower() + " "
    # Replace common punctuation with spaces for cleaner boundary matching
    cleaned_text = re.sub(r'[,;()\[\]{}|/\\]', ' ', lower_text)

    for canonical, info in SKILLS_TAXONOMY.items():
        aliases = info.get("aliases", [canonical.lower()])
        for alias in aliases:
            # Match whole word / boundary
            pattern = r'(?<![a-zA-Z0-9_\-\.])' + re.escape(alias.lower()) + r'(?![a-zA-Z0-9_\-\.])'
            if re.search(pattern, cleaned_text):
                found_skills.add(canonical)
                break

    # If spaCy is loaded, check named entities and noun chunks for potential skills
    nlp = get_spacy_nlp()
    if nlp and len(text) < 100000:
        try:
            doc = nlp(text[:10000])
            for ent in doc.ents:
                if ent.label_ in ("PRODUCT", "ORG", "LANGUAGE"):
                    cand = ent.text.strip()
                    if cand in SKILLS_TAXONOMY:
                        found_skills.add(cand)
        except Exception as e:
            logger.debug(f"spaCy entity inspection skipped: {e}")

    return sorted(list(found_skills))

def get_skill_metadata(skill_name: str) -> Dict:
    """Returns category, default description, and details for a skill."""
    if skill_name in SKILLS_TAXONOMY:
        return SKILLS_TAXONOMY[skill_name]
    
    # Heuristic fallback for custom or unlisted skills
    return {
        "category": "Technical Competency",
        "aliases": [skill_name.lower()],
        "description": f"Proficiency in {skill_name} application, implementation, and best practices."
    }
