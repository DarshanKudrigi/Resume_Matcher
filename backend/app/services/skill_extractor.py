import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy: canonical_name -> {category, aliases, description}
SKILLS_TAXONOMY: Dict[str, Dict] = {
    # Core Frontend
    "JavaScript": {
        "category": "Core Frontend",
        "aliases": ["javascript", "js", "es6", "es6+", "ecmascript"],
        "description": "Demonstrated through modern ES6+ projects, async programming, and state management."
    },
    "TypeScript": {
        "category": "Core Frontend",
        "aliases": ["typescript", "ts"],
        "description": "Strict type safety, generic interfaces, and enterprise frontend architecture."
    },
    "React": {
        "category": "Core Frontend",
        "aliases": ["react", "react.js", "reactjs", "react hooks"],
        "description": "Functional components, custom hooks, virtual DOM, and component lifecycles."
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
    "Tailwind CSS": {
        "category": "Core Frontend",
        "aliases": ["tailwind", "tailwindcss", "tailwind-css"],
        "description": "Utility-first modern styling, responsive variants, and dark theme support."
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
        "description": "Dependency injection, RxJS streams, and component architecture."
    },
    "Redux": {
        "category": "Core Frontend",
        "aliases": ["redux", "redux toolkit", "rtk"],
        "description": "Global predictable state container, selectors, and async middleware."
    },
    "GraphQL": {
        "category": "Backend / APIs",
        "aliases": ["graphql", "apollo client", "apollo server"],
        "description": "Schema definition, queries, mutations, and client cache normalization."
    },

    # Backend / APIs
    "Node.js": {
        "category": "Backend / APIs",
        "aliases": ["node", "node.js", "nodejs"],
        "description": "REST endpoint creation, Express server integration, and event loop handling."
    },
    "Python": {
        "category": "Backend / APIs",
        "aliases": ["python", "python3", "py"],
        "description": "Backend services, scripting, automation, and data structures."
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
        "description": "Battery-included web framework, ORM models, and secure authentication."
    },
    "Java": {
        "category": "Backend / APIs",
        "aliases": ["java", "spring", "spring boot"],
        "description": "Object-oriented backend services, Spring Boot, and enterprise microservices."
    },
    "Go": {
        "category": "Backend / APIs",
        "aliases": ["golang", "go"],
        "description": "Concurrent goroutines, microservice architectures, and high-throughput network services."
    },
    "REST APIs": {
        "category": "Backend / APIs",
        "aliases": ["rest", "rest api", "rest apis", "restful", "restful apis"],
        "description": "HTTP method semantics, resource-based design, and JSON payload handling."
    },

    # Databases
    "SQL": {
        "category": "Databases & Storage",
        "aliases": ["sql", "relational database", "rdbms"],
        "description": "Relational querying, joins, aggregations, indexing, and normalization."
    },
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

    # Architecture & Concepts
    "System Design": {
        "category": "Architecture",
        "aliases": ["system design", "distributed systems", "scalability", "architecture", "microservices"],
        "description": "High-level caching, CDN edge delivery, rate limiting, and frontend architecture."
    },
    "Data Structures": {
        "category": "Foundations",
        "aliases": ["data structures", "algorithms", "dsa"],
        "description": "Arrays, trees, graphs, hashing, and asymptotic algorithmic complexity."
    },
    "Testing": {
        "category": "Quality Assurance",
        "aliases": ["jest", "cypress", "playwright", "vitest", "unit test", "unit testing"],
        "description": "Unit testing, end-to-end user flows, test assertions, and mock coverage."
    }
}

def extract_skills_from_text(text: str) -> List[str]:
    """Scans text and returns canonical skill names present in the content."""
    if not text:
        return []
    
    found_skills: Set[str] = set()
    lower_text = " " + text.lower() + " "
    # Replace common punctuation with spaces for cleaner boundary matching
    cleaned_text = re.sub(r'[,;()\[\]{}|/]', ' ', lower_text)

    for canonical, info in SKILLS_TAXONOMY.items():
        aliases = info.get("aliases", [canonical.lower()])
        for alias in aliases:
            # Match whole word / boundary
            pattern = r'(?<![a-zA-Z0-9_\-\.])' + re.escape(alias.lower()) + r'(?![a-zA-Z0-9_\-\.])'
            if re.search(pattern, cleaned_text):
                found_skills.add(canonical)
                break

    # Preserve canonical ordering or alphabetized
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
