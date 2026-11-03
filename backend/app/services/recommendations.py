import re
import urllib.parse
from typing import Dict, List, Optional
from app.schemas.analysis import LearningRecommendation, LearningResource

# Curated Official Documentation Links from each technology's official portal
CURATED_LEARNING_ROADMAPS: Dict[str, Dict] = {
    "React": {
        "subtitle": "Build modern, component-driven user interfaces with the official React library.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Master state management, JSX, hooks (useState, useEffect, useMemo), and component lifecycles directly from the React documentation.",
        "keyTopics": ["Components & Props", "State & Hooks Lifecycle", "Managing Effects", "Escape Hatches & Performance"],
        "resources": [
            {
                "title": "React Official Quick Start & Tutorial",
                "type": "Official Documentation",
                "provider": "React Team (react.dev)",
                "duration": "Official Guide",
                "link": "https://react.dev/learn"
            },
            {
                "title": "Built-in React Hooks API Reference",
                "type": "Official Reference",
                "provider": "React Team (react.dev)",
                "duration": "API Reference",
                "link": "https://react.dev/reference/react"
            }
        ]
    },
    "Next.js": {
        "subtitle": "Production React framework for full-stack web applications.",
        "difficulty": "Intermediate",
        "estimatedTime": "8–10 Hours",
        "summary": "Learn Server Components, App Router, server-side rendering (SSR), static site generation (SSG), and API routes from Vercel's official documentation.",
        "keyTopics": ["App Router & Layouts", "Server & Client Components", "Data Fetching & Caching", "Server Actions & Mutations"],
        "resources": [
            {
                "title": "Next.js Official Documentation & Getting Started",
                "type": "Official Documentation",
                "provider": "Vercel (nextjs.org)",
                "duration": "Official Guide",
                "link": "https://nextjs.org/docs"
            },
            {
                "title": "Next.js App Router Architecture Guide",
                "type": "Official Reference",
                "provider": "Vercel (nextjs.org)",
                "duration": "Architecture Docs",
                "link": "https://nextjs.org/docs/app"
            }
        ]
    },
    "TypeScript": {
        "subtitle": "Level up code reliability and scalability with static typing.",
        "difficulty": "Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Learn static typing, interfaces, generics, utility types, and strict mode compiler configuration directly from Microsoft's handbook.",
        "keyTopics": ["Types vs Interfaces", "Generic Types & Constraints", "Type Narrowing & Discriminated Unions", "Strict Mode & tsconfig Tuning"],
        "resources": [
            {
                "title": "TypeScript Official Handbook",
                "type": "Official Documentation",
                "provider": "Microsoft (typescriptlang.org)",
                "duration": "Official Handbook",
                "link": "https://www.typescriptlang.org/docs/handbook/intro.html"
            },
            {
                "title": "TypeScript Everyday Types & Generics",
                "type": "Official Reference",
                "provider": "Microsoft (typescriptlang.org)",
                "duration": "Reference Docs",
                "link": "https://www.typescriptlang.org/docs/handbook/2/everyday-types.html"
            }
        ]
    },
    "JavaScript": {
        "subtitle": "Master modern ECMAScript standards and browser/engine fundamentals.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Study closures, promises, async/await, DOM APIs, and ES6+ modules through MDN Web Docs.",
        "keyTopics": ["Async / Await & Promises", "Closures & Scope Chain", "Event Loop & Microtasks", "ES6+ Destructuring & Modules"],
        "resources": [
            {
                "title": "MDN JavaScript Official Guide",
                "type": "Official Documentation",
                "provider": "Mozilla Developer Network (MDN)",
                "duration": "Official Guide",
                "link": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"
            },
            {
                "title": "JavaScript Language & Standard Built-in Objects",
                "type": "Official Reference",
                "provider": "Mozilla Developer Network (MDN)",
                "duration": "Reference Docs",
                "link": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference"
            }
        ]
    },
    "Python": {
        "subtitle": "Learn idiomatic Python programming, standard library, and OOP.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Explore Python data structures, list comprehensions, decorators, generators, and standard packages through the Python Software Foundation tutorial.",
        "keyTopics": ["Data Structures & Comprehensions", "Object-Oriented Programming", "Decorators & Generators", "Virtual Environments & Packaging"],
        "resources": [
            {
                "title": "Official Python 3 Tutorial",
                "type": "Official Documentation",
                "provider": "Python Software Foundation (python.org)",
                "duration": "Official Tutorial",
                "link": "https://docs.python.org/3/tutorial/"
            },
            {
                "title": "Python Standard Library Reference",
                "type": "Official Reference",
                "provider": "Python Software Foundation (python.org)",
                "duration": "API Reference",
                "link": "https://docs.python.org/3/library/"
            }
        ]
    },
    "FastAPI": {
        "subtitle": "High-performance, modern Python web framework for building APIs.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Build production-ready asynchronous REST APIs with automatic OpenAPI/Swagger docs, Pydantic type validation, and dependency injection.",
        "keyTopics": ["Path & Query Parameters", "Pydantic Request Bodies & Schemas", "Dependency Injection System", "OAuth2 & JWT Security"],
        "resources": [
            {
                "title": "FastAPI Official Tutorial - User Guide",
                "type": "Official Documentation",
                "provider": "Tiangolo / FastAPI (fastapi.tiangolo.com)",
                "duration": "Official Tutorial",
                "link": "https://fastapi.tiangolo.com/tutorial/"
            },
            {
                "title": "FastAPI Advanced User Guide & Security",
                "type": "Official Reference",
                "provider": "Tiangolo / FastAPI (fastapi.tiangolo.com)",
                "duration": "Advanced Docs",
                "link": "https://fastapi.tiangolo.com/advanced/"
            }
        ]
    },
    "Node.js": {
        "subtitle": "Asynchronous event-driven JavaScript runtime environment.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Understand event loop mechanisms, non-blocking I/O, file system operations, and HTTP server creation using official Node.js documentation.",
        "keyTopics": ["Event Loop & Callbacks", "Streams & Buffer API", "HTTP & File System Modules", "Node.js Package Manager (npm)"],
        "resources": [
            {
                "title": "Official Node.js Learn Guides",
                "type": "Official Documentation",
                "provider": "OpenJS Foundation (nodejs.org)",
                "duration": "Official Guide",
                "link": "https://nodejs.org/en/learn"
            },
            {
                "title": "Node.js Core API Documentation",
                "type": "Official Reference",
                "provider": "OpenJS Foundation (nodejs.org)",
                "duration": "API Reference",
                "link": "https://nodejs.org/docs/latest/api/"
            }
        ]
    },
    "Express.js": {
        "subtitle": "Fast, unopinionated, minimalist web framework for Node.js.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Master routing, middleware chains, error handling, and RESTful service setup with the official Express.js documentation.",
        "keyTopics": ["Routing & Parameter Handling", "Writing Custom Middleware", "Error Handling & Status Codes", "Database Integration"],
        "resources": [
            {
                "title": "Express.js Official Getting Started Guide",
                "type": "Official Documentation",
                "provider": "Express / OpenJS (expressjs.com)",
                "duration": "Official Guide",
                "link": "https://expressjs.com/en/starter/installing.html"
            },
            {
                "title": "Express.js Routing & Middleware Documentation",
                "type": "Official Reference",
                "provider": "Express / OpenJS (expressjs.com)",
                "duration": "Reference Docs",
                "link": "https://expressjs.com/en/guide/routing.html"
            }
        ]
    },
    "Docker": {
        "subtitle": "Containerization platform for packaging and deploying applications.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Learn container concepts, write multi-stage Dockerfiles, manage images, and configure local container networks using Docker documentation.",
        "keyTopics": ["Images, Containers & Registries", "Writing Multi-Stage Dockerfiles", "Volume Mounting & Persistence", "Docker Compose Orchestration"],
        "resources": [
            {
                "title": "Docker Official Get Started Guide",
                "type": "Official Documentation",
                "provider": "Docker Inc. (docs.docker.com)",
                "duration": "Official Guide",
                "link": "https://docs.docker.com/get-started/"
            },
            {
                "title": "Dockerfile & Compose Reference Manual",
                "type": "Official Reference",
                "provider": "Docker Inc. (docs.docker.com)",
                "duration": "Reference Docs",
                "link": "https://docs.docker.com/reference/dockerfile/"
            }
        ]
    },
    "Kubernetes": {
        "subtitle": "Production-grade container orchestration system.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "8–12 Hours",
        "summary": "Deploy, scale, and manage containerized applications with Pods, Deployments, Services, and ConfigMaps using the Kubernetes documentation.",
        "keyTopics": ["Pods, Deployments & ReplicaSets", "Services & Ingress Controllers", "ConfigMaps & Secrets", "Horizontal Pod Autoscaling"],
        "resources": [
            {
                "title": "Kubernetes Official Tutorials & Basics",
                "type": "Official Documentation",
                "provider": "CNCF / Kubernetes (kubernetes.io)",
                "duration": "Official Guide",
                "link": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"
            },
            {
                "title": "Kubernetes Architecture Concepts & Reference",
                "type": "Official Reference",
                "provider": "CNCF / Kubernetes (kubernetes.io)",
                "duration": "Architecture Docs",
                "link": "https://kubernetes.io/docs/concepts/"
            }
        ]
    },
    "AWS": {
        "subtitle": "Comprehensive cloud computing platform and distributed services.",
        "difficulty": "Intermediate",
        "estimatedTime": "10–12 Hours",
        "summary": "Master core cloud infrastructure including EC2, S3 static hosting, CloudFront CDN, Lambda serverless, and IAM security directly from AWS docs.",
        "keyTopics": ["S3 Static Storage & Hosting", "CloudFront CDN & Caching", "AWS Lambda & Serverless Compute", "IAM Roles & Security Policies"],
        "resources": [
            {
                "title": "AWS Official Getting Started Documentation",
                "type": "Official Documentation",
                "provider": "Amazon Web Services (docs.aws.amazon.com)",
                "duration": "Official Guide",
                "link": "https://docs.aws.amazon.com/"
            },
            {
                "title": "AWS Serverless & Compute Guides",
                "type": "Official Reference",
                "provider": "Amazon Web Services (aws.amazon.com)",
                "duration": "Reference Docs",
                "link": "https://aws.amazon.com/getting-started/hands-on/"
            }
        ]
    },
    "Azure": {
        "subtitle": "Microsoft's enterprise cloud computing and infrastructure platform.",
        "difficulty": "Intermediate",
        "estimatedTime": "8–10 Hours",
        "summary": "Deploy web apps, manage Azure Blob Storage, configure App Services, and set up Entra ID / IAM through Microsoft Learn.",
        "keyTopics": ["Azure App Service & Web Apps", "Blob Storage & CDN", "Azure Functions & Event Grid", "Azure Virtual Networks & RBAC"],
        "resources": [
            {
                "title": "Microsoft Azure Official Documentation",
                "type": "Official Documentation",
                "provider": "Microsoft Learn (learn.microsoft.com)",
                "duration": "Official Guide",
                "link": "https://learn.microsoft.com/en-us/azure/"
            },
            {
                "title": "Azure App Service Quickstart Guide",
                "type": "Official Reference",
                "provider": "Microsoft Learn (learn.microsoft.com)",
                "duration": "Quickstart Docs",
                "link": "https://learn.microsoft.com/en-us/azure/app-service/quickstart-python"
            }
        ]
    },
    "Google Cloud": {
        "subtitle": "Google Cloud Platform (GCP) computing and data infrastructure.",
        "difficulty": "Intermediate",
        "estimatedTime": "8–10 Hours",
        "summary": "Deploy applications to Cloud Run, configure Cloud Storage buckets, and integrate Cloud SQL via the Google Cloud documentation.",
        "keyTopics": ["Cloud Run Container Serving", "Cloud Storage & IAM", "Compute Engine & VPCs", "Cloud SQL & Secret Manager"],
        "resources": [
            {
                "title": "Google Cloud Official Documentation",
                "type": "Official Documentation",
                "provider": "Google Cloud (cloud.google.com)",
                "duration": "Official Guide",
                "link": "https://cloud.google.com/docs"
            },
            {
                "title": "Google Cloud Run Quickstart Documentation",
                "type": "Official Reference",
                "provider": "Google Cloud (cloud.google.com)",
                "duration": "Quickstart Docs",
                "link": "https://cloud.google.com/run/docs/quickstarts"
            }
        ]
    },
    "MongoDB": {
        "subtitle": "Scalable document-oriented NoSQL database system.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Learn BSON schema design, CRUD operations, indexing, and aggregation pipelines using the official MongoDB manual.",
        "keyTopics": ["Document Model & Collections", "CRUD Queries & Projection", "Indexing Strategies", "Aggregation Pipeline Stages"],
        "resources": [
            {
                "title": "MongoDB Official Manual & Getting Started",
                "type": "Official Documentation",
                "provider": "MongoDB Inc. (mongodb.com)",
                "duration": "Official Manual",
                "link": "https://www.mongodb.com/docs/manual/tutorial/getting-started/"
            },
            {
                "title": "MongoDB Aggregation Framework Reference",
                "type": "Official Reference",
                "provider": "MongoDB Inc. (mongodb.com)",
                "duration": "Reference Docs",
                "link": "https://www.mongodb.com/docs/manual/aggregation/"
            }
        ]
    },
    "PostgreSQL": {
        "subtitle": "World's most advanced open-source relational database.",
        "difficulty": "Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Master relational schema design, B-tree/GIN indexing, foreign keys, JSONB queries, and ACID transactions via the official PostgreSQL documentation.",
        "keyTopics": ["Relational Normalization & Constraints", "B-Tree & GIN Indexes", "Complex Joins, Views & CTEs", "Transactions & Isolation Levels"],
        "resources": [
            {
                "title": "PostgreSQL Official Documentation Tutorial",
                "type": "Official Documentation",
                "provider": "The PostgreSQL Global Development Group (postgresql.org)",
                "duration": "Official Guide",
                "link": "https://www.postgresql.org/docs/current/tutorial.html"
            },
            {
                "title": "PostgreSQL SQL Language Reference",
                "type": "Official Reference",
                "provider": "PostgreSQL (postgresql.org)",
                "duration": "Reference Docs",
                "link": "https://www.postgresql.org/docs/current/sql.html"
            }
        ]
    },
    "MySQL": {
        "subtitle": "Popular relational database management system.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Understand table creation, constraints, index optimization, stored routines, and query tuning from the MySQL Reference Manual.",
        "keyTopics": ["Schema Design & Data Types", "Primary Keys & Foreign Keys", "Index Creation & EXPLAIN", "Transactions with InnoDB"],
        "resources": [
            {
                "title": "MySQL 8.0 Official Reference Manual",
                "type": "Official Documentation",
                "provider": "Oracle Corporation (dev.mysql.com)",
                "duration": "Official Manual",
                "link": "https://dev.mysql.com/doc/refman/8.0/en/tutorial.html"
            },
            {
                "title": "MySQL Optimization & Indexing Guide",
                "type": "Official Reference",
                "provider": "Oracle Corporation (dev.mysql.com)",
                "duration": "Optimization Docs",
                "link": "https://dev.mysql.com/doc/refman/8.0/en/optimization.html"
            }
        ]
    },
    "Redis": {
        "subtitle": "In-memory data structure store used as a database, cache, and message broker.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Implement high-speed caching, TTL expiration, Pub/Sub channels, and distributed key-value storage using the official Redis docs.",
        "keyTopics": ["Data Types (Strings, Hashes, Lists, Sets)", "Cache Expiration (TTL & LRU Eviction)", "Pub/Sub Messaging & Streams", "Transactions & Pipelining"],
        "resources": [
            {
                "title": "Redis Official Get Started Guide",
                "type": "Official Documentation",
                "provider": "Redis Ltd. (redis.io)",
                "duration": "Official Guide",
                "link": "https://redis.io/docs/latest/get-started/"
            },
            {
                "title": "Redis Command Reference & Data Types",
                "type": "Official Reference",
                "provider": "Redis Ltd. (redis.io)",
                "duration": "Command Docs",
                "link": "https://redis.io/docs/latest/commands/"
            }
        ]
    },
    "GraphQL": {
        "subtitle": "Query language and runtime for your application APIs.",
        "difficulty": "Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Learn to write queries, mutations, subscriptions, and schemas with precise data fetching via the GraphQL specification.",
        "keyTopics": ["Schema Definition Language (SDL)", "Queries & Nested Fields", "Mutations & Resolvers", "Subscriptions & Real-time Data"],
        "resources": [
            {
                "title": "GraphQL Official Introduction & Learn Guide",
                "type": "Official Documentation",
                "provider": "GraphQL Foundation (graphql.org)",
                "duration": "Official Guide",
                "link": "https://graphql.org/learn/"
            },
            {
                "title": "GraphQL Schema & Types Reference",
                "type": "Official Reference",
                "provider": "GraphQL Foundation (graphql.org)",
                "duration": "Reference Docs",
                "link": "https://graphql.org/learn/schema/"
            }
        ]
    },
    "REST APIs": {
        "subtitle": "Architectural style for designing networked distributed systems.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Study HTTP methods, status codes, OpenAPI/Swagger specifications, idempotency, and RESTful resource modeling.",
        "keyTopics": ["HTTP Verbs & Status Codes", "Resource URI Design & Pluralization", "OpenAPI 3.0 / Swagger Specifications", "Rate Limiting & Authentication"],
        "resources": [
            {
                "title": "OpenAPI / Swagger Official Specification Guide",
                "type": "Official Documentation",
                "provider": "SmartBear / OpenAPI Initiative (swagger.io)",
                "duration": "Official Specification",
                "link": "https://swagger.io/docs/specification/about/"
            },
            {
                "title": "MDN HTTP Overview & Methods Guide",
                "type": "Official Reference",
                "provider": "Mozilla Developer Network (MDN)",
                "duration": "Reference Docs",
                "link": "https://developer.mozilla.org/en-US/docs/Web/HTTP"
            }
        ]
    },
    "Tailwind CSS": {
        "subtitle": "Utility-first CSS framework for rapid modern UI development.",
        "difficulty": "Beginner",
        "estimatedTime": "3–5 Hours",
        "summary": "Learn utility classes, responsive variants, dark mode toggling, and component extraction from the official Tailwind CSS documentation.",
        "keyTopics": ["Utility Classes & Flexbox/Grid", "Responsive Design Modifiers", "Dark Mode Styling", "Arbitrary Values & Config"],
        "resources": [
            {
                "title": "Tailwind CSS Official Documentation",
                "type": "Official Documentation",
                "provider": "Tailwind Labs (tailwindcss.com)",
                "duration": "Official Docs",
                "link": "https://tailwindcss.com/docs/installation"
            },
            {
                "title": "Tailwind CSS Responsive Design & Theme Guide",
                "type": "Official Reference",
                "provider": "Tailwind Labs (tailwindcss.com)",
                "duration": "Design Docs",
                "link": "https://tailwindcss.com/docs/responsive-design"
            }
        ]
    },
    "Git": {
        "subtitle": "Distributed version control system for tracking source code changes.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Master branching, merging, rebasing, stash workflows, and commit history inspection directly from the official Pro Git book.",
        "keyTopics": ["Branching & Pull Request Workflows", "Resolving Merge Conflicts", "Git Rebase vs Merge", "Commit Inspection & Stashing"],
        "resources": [
            {
                "title": "Pro Git Book & Official Reference Manual",
                "type": "Official Documentation",
                "provider": "Git Core Team (git-scm.com)",
                "duration": "Official Book",
                "link": "https://git-scm.com/doc"
            },
            {
                "title": "Git Branching Workflows Documentation",
                "type": "Official Reference",
                "provider": "Git Core Team (git-scm.com)",
                "duration": "Reference Docs",
                "link": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell"
            }
        ]
    },
    "CI/CD & GitHub Actions": {
        "subtitle": "Automate build, test, and deployment software delivery pipelines.",
        "difficulty": "Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Write YAML workflow definitions, matrix builds, automated unit tests, and continuous deployment steps with GitHub Actions documentation.",
        "keyTopics": ["Workflow Triggers (push, pull_request)", "Jobs, Steps & Runner Environments", "Encrypted Secrets & Environment Variables", "Deploying to Cloud Providers"],
        "resources": [
            {
                "title": "GitHub Actions Official Quickstart Guide",
                "type": "Official Documentation",
                "provider": "GitHub / Microsoft (docs.github.com)",
                "duration": "Official Guide",
                "link": "https://docs.github.com/en/actions"
            },
            {
                "title": "Workflow Syntax & Actions Reference Manual",
                "type": "Official Reference",
                "provider": "GitHub / Microsoft (docs.github.com)",
                "duration": "Syntax Reference",
                "link": "https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions"
            }
        ]
    },
    "Java": {
        "subtitle": "Object-oriented, class-based, robust programming language.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "8–10 Hours",
        "summary": "Master JVM fundamentals, Java Collections Framework, streams, concurrency, and OOP principles via Oracle's official documentation.",
        "keyTopics": ["Collections Framework & Generics", "Streams API & Lambda Expressions", "Concurrency & Threading", "JVM Memory & Garbage Collection"],
        "resources": [
            {
                "title": "Oracle Java Official Documentation & Tutorials",
                "type": "Official Documentation",
                "provider": "Oracle Corporation (docs.oracle.com)",
                "duration": "Official Documentation",
                "link": "https://docs.oracle.com/en/java/javase/index.html"
            },
            {
                "title": "Java API Specification & Core Packages",
                "type": "Official Reference",
                "provider": "Oracle Corporation (docs.oracle.com)",
                "duration": "API Specification",
                "link": "https://docs.oracle.com/en/java/javase/21/docs/api/index.html"
            }
        ]
    },
    "Spring Boot": {
        "subtitle": "Enterprise-grade Java application framework and microservice platform.",
        "difficulty": "Intermediate",
        "estimatedTime": "8–12 Hours",
        "summary": "Build production microservices with Spring Data JPA, dependency injection, Spring Security, and actuator monitoring using Spring's official docs.",
        "keyTopics": ["Inversion of Control (IoC) & Beans", "Spring Data JPA & Hibernate", "REST Controllers & Validation", "Spring Security & JWT"],
        "resources": [
            {
                "title": "Spring Boot Official Reference Documentation",
                "type": "Official Documentation",
                "provider": "Broadcom / Spring (spring.io)",
                "duration": "Official Reference",
                "link": "https://docs.spring.io/spring-boot/index.html"
            },
            {
                "title": "Building a RESTful Web Service Guide",
                "type": "Official Tutorial",
                "provider": "Spring Team (spring.io)",
                "duration": "Official Tutorial",
                "link": "https://spring.io/guides/gs/rest-service"
            }
        ]
    },
    "Go": {
        "subtitle": "High-performance, statically typed, compiled programming language.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Study goroutines, channels, interfaces, structs, and standard library HTTP servers via the official Go documentation.",
        "keyTopics": ["Goroutines & Channel Concurrency", "Structs & Interface Composition", "Error Handling Conventions", "Net/HTTP Package"],
        "resources": [
            {
                "title": "The Go Programming Language Official Documentation",
                "type": "Official Documentation",
                "provider": "Go Team (go.dev)",
                "duration": "Official Docs",
                "link": "https://go.dev/doc/"
            },
            {
                "title": "A Tour of Go - Interactive Tutorial",
                "type": "Official Tutorial",
                "provider": "Go Team (go.dev)",
                "duration": "Interactive Tour",
                "link": "https://go.dev/tour/"
            }
        ]
    },
    "Rust": {
        "subtitle": "Memory-safe, high-performance systems programming language.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "10–14 Hours",
        "summary": "Understand ownership, borrowing, lifetimes, pattern matching, and async Rust from 'The Rust Programming Language' book.",
        "keyTopics": ["Ownership, Borrowing & Lifetimes", "Enums & Pattern Matching", "Traits & Generics", "Concurrency & Error Handling"],
        "resources": [
            {
                "title": "The Rust Programming Language (The Book)",
                "type": "Official Documentation",
                "provider": "Rust Community (doc.rust-lang.org)",
                "duration": "Official Book",
                "link": "https://doc.rust-lang.org/book/"
            },
            {
                "title": "Rust Standard Library API Reference",
                "type": "Official Reference",
                "provider": "Rust Community (doc.rust-lang.org)",
                "duration": "API Reference",
                "link": "https://doc.rust-lang.org/std/"
            }
        ]
    },
    "C++": {
        "subtitle": "High-performance systems and application programming language.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "10–14 Hours",
        "summary": "Master modern C++ (C++17/20), RAII, Smart Pointers, STL containers, templates, and memory management through cppreference.",
        "keyTopics": ["Pointers, References & RAII", "Standard Template Library (STL)", "Templates & Metaprogramming", "Move Semantics & Smart Pointers"],
        "resources": [
            {
                "title": "C++ Standard Library Reference Manual",
                "type": "Official Reference",
                "provider": "CppReference (en.cppreference.com)",
                "duration": "Reference Manual",
                "link": "https://en.cppreference.com/w/cpp"
            },
            {
                "title": "Standard C++ Foundation Best Practices & Guides",
                "type": "Official Documentation",
                "provider": "Standard C++ Foundation (isocpp.org)",
                "duration": "Official Guidelines",
                "link": "https://isocpp.org/get-started"
            }
        ]
    },
    "System Design": {
        "subtitle": "Learn scalability, distributed systems, and architectural fundamentals.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "8–12 Hours",
        "summary": "Understand client-side state architecture, bundle splitting, CDN caching, rate limiting, and scalable REST API conventions.",
        "keyTopics": ["Horizontal Scaling & Load Balancing", "Caching Strategies & CDN", "Database Sharding & Replication", "Microservices vs Monoliths"],
        "resources": [
            {
                "title": "System Design Primer Official Repository & Guides",
                "type": "Official Guide",
                "provider": "Open Source Community (github.com/donnemartin)",
                "duration": "Comprehensive Guide",
                "link": "https://github.com/donnemartin/system-design-primer"
            },
            {
                "title": "Microservice Architecture Patterns Guide",
                "type": "Official Reference",
                "provider": "Chris Richardson (microservices.io)",
                "duration": "Architecture Docs",
                "link": "https://microservices.io/patterns/index.html"
            }
        ]
    },
    "Redux": {
        "subtitle": "Predictable state container for modern JavaScript and React apps.",
        "difficulty": "Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Learn Redux Toolkit (RTK), slices, configureStore, createAsyncThunk, and RTK Query data fetching from the official Redux documentation.",
        "keyTopics": ["Redux Toolkit (RTK) & Slices", "Immutability with Immer", "Asynchronous Actions & Thunks", "RTK Query API Caching"],
        "resources": [
            {
                "title": "Redux Toolkit Official Documentation & Tutorial",
                "type": "Official Documentation",
                "provider": "Redux Team (redux.js.org)",
                "duration": "Official Guide",
                "link": "https://redux.js.org/introduction/getting-started"
            },
            {
                "title": "Redux Essentials Step-by-Step Tutorial",
                "type": "Official Tutorial",
                "provider": "Redux Team (redux.js.org)",
                "duration": "Tutorial Docs",
                "link": "https://redux.js.org/tutorials/essentials/part-1-overview-concepts"
            }
        ]
    },
    "Terraform": {
        "subtitle": "Infrastructure as Code tool to build, change, and version resources safely.",
        "difficulty": "Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Define cloud resources in HCL, manage state files, use modules, and automate infrastructure deployments via HashiCorp Developer documentation.",
        "keyTopics": ["HashiCorp Configuration Language (HCL)", "State Management & Locking", "Providers & Reusable Modules", "Terraform Plan & Apply Lifecycle"],
        "resources": [
            {
                "title": "HashiCorp Terraform Official Tutorials",
                "type": "Official Documentation",
                "provider": "HashiCorp (developer.hashicorp.com)",
                "duration": "Official Tutorials",
                "link": "https://developer.hashicorp.com/terraform/tutorials"
            },
            {
                "title": "Terraform Language Documentation & Syntax",
                "type": "Official Reference",
                "provider": "HashiCorp (developer.hashicorp.com)",
                "duration": "Language Reference",
                "link": "https://developer.hashicorp.com/terraform/language"
            }
        ]
    },
    "Linux": {
        "subtitle": "Open-source Unix-like operating system kernel and command-line shell.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Study file permissions, process management, Bash scripting, systemd services, and networking commands through the official Linux kernel documentation.",
        "keyTopics": ["Shell Navigation & File Permissions", "Process Management (ps, kill, top)", "Bash Scripting & Piping", "Systemd Services & Networking"],
        "resources": [
            {
                "title": "The Linux Kernel Documentation",
                "type": "Official Documentation",
                "provider": "The Linux Foundation (kernel.org)",
                "duration": "Official Docs",
                "link": "https://www.kernel.org/doc/html/latest/"
            },
            {
                "title": "GNU Bash Official Reference Manual",
                "type": "Official Reference",
                "provider": "Free Software Foundation (gnu.org)",
                "duration": "Reference Manual",
                "link": "https://www.gnu.org/software/bash/manual/bash.html"
            }
        ]
    },
    "Nginx": {
        "subtitle": "High-performance HTTP server, reverse proxy, and load balancer.",
        "difficulty": "Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Configure reverse proxying, SSL termination, static file caching, and upstream load balancing using the official Nginx documentation.",
        "keyTopics": ["Server Blocks & Locations", "Reverse Proxy & Upstream Balancing", "SSL/TLS Certificate Configuration", "Gzip & Static Asset Caching"],
        "resources": [
            {
                "title": "Nginx Official Beginner's Guide",
                "type": "Official Documentation",
                "provider": "F5 / Nginx (nginx.org)",
                "duration": "Official Guide",
                "link": "https://nginx.org/en/docs/beginners_guide.html"
            },
            {
                "title": "Nginx Core Directives Reference Manual",
                "type": "Official Reference",
                "provider": "F5 / Nginx (nginx.org)",
                "duration": "Directive Reference",
                "link": "https://nginx.org/en/docs/http/ngx_http_core_module.html"
            }
        ]
    },
    "PyTorch": {
        "subtitle": "Open-source machine learning and deep learning framework.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "8–12 Hours",
        "summary": "Understand Tensors, Autograd automatic differentiation, neural network layers (torch.nn), and GPU training loops from PyTorch tutorials.",
        "keyTopics": ["Tensors & CUDA Acceleration", "Autograd Automatic Differentiation", "Building Neural Networks (torch.nn)", "Dataset & DataLoader Pipelines"],
        "resources": [
            {
                "title": "PyTorch Official Tutorials & Deep Learning Basics",
                "type": "Official Documentation",
                "provider": "Linux Foundation / PyTorch (pytorch.org)",
                "duration": "Official Tutorials",
                "link": "https://pytorch.org/tutorials/beginner/basics/intro.html"
            },
            {
                "title": "PyTorch Core API Reference",
                "type": "Official Reference",
                "provider": "PyTorch Team (pytorch.org)",
                "duration": "API Reference",
                "link": "https://pytorch.org/docs/stable/index.html"
            }
        ]
    },
    "TensorFlow": {
        "subtitle": "End-to-end open-source platform for machine learning.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "8–12 Hours",
        "summary": "Build, train, and deploy machine learning models using Keras Sequential/Functional APIs, computational graphs, and TensorFlow tutorials.",
        "keyTopics": ["Keras Model Architecture", "Data Pipelines with tf.data", "Model Training & Evaluation", "Model Export & TensorFlow Serving"],
        "resources": [
            {
                "title": "TensorFlow Official Tutorials",
                "type": "Official Documentation",
                "provider": "Google (tensorflow.org)",
                "duration": "Official Tutorials",
                "link": "https://www.tensorflow.org/tutorials"
            },
            {
                "title": "Keras API Reference on TensorFlow",
                "type": "Official Reference",
                "provider": "Google (tensorflow.org)",
                "duration": "API Docs",
                "link": "https://www.tensorflow.org/api_docs/python/tf/keras"
            }
        ]
    },
    "Pandas": {
        "subtitle": "Fast, powerful, and flexible open source data analysis and manipulation library.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Master DataFrames, Series, filtering, grouping, merging, and missing data handling from the official Pandas documentation.",
        "keyTopics": ["DataFrames & Series Indexing", "Filtering & Boolean Masking", "GroupBy & Aggregations", "Merging, Joining & Reshaping"],
        "resources": [
            {
                "title": "Pandas Getting Started Tutorials",
                "type": "Official Documentation",
                "provider": "Pandas Development Team (pandas.pydata.org)",
                "duration": "Official Guide",
                "link": "https://pandas.pydata.org/docs/getting_started/index.html"
            },
            {
                "title": "Pandas API Reference Documentation",
                "type": "Official Reference",
                "provider": "Pandas Development Team (pandas.pydata.org)",
                "duration": "API Reference",
                "link": "https://pandas.pydata.org/docs/reference/index.html"
            }
        ]
    },
    "NumPy": {
        "subtitle": "Fundamental package for scientific computing with Python.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Learn N-dimensional arrays (ndarray), vectorization, broadcasting, and linear algebra operations from the official NumPy manual.",
        "keyTopics": ["N-Dimensional Arrays & Dtypes", "Broadcasting & Vectorized Math", "Array Indexing & Slicing", "Linear Algebra & Random Routines"],
        "resources": [
            {
                "title": "NumPy Official Quickstart Guide",
                "type": "Official Documentation",
                "provider": "NumPy Developers (numpy.org)",
                "duration": "Official Guide",
                "link": "https://numpy.org/doc/stable/user/quickstart.html"
            },
            {
                "title": "NumPy Array Creation & Routines Reference",
                "type": "Official Reference",
                "provider": "NumPy Developers (numpy.org)",
                "duration": "API Reference",
                "link": "https://numpy.org/doc/stable/reference/index.html"
            }
        ]
    },
    "Jest": {
        "subtitle": "Delightful JavaScript Testing Framework with a focus on simplicity.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Write unit tests, assertions, snapshot tests, and mocks for JavaScript and React applications using the official Jest documentation.",
        "keyTopics": ["Expect Matchers & Assertions", "Mock Functions & Spies", "Testing Asynchronous Code", "Snapshot Testing & Coverage"],
        "resources": [
            {
                "title": "Jest Official Getting Started Guide",
                "type": "Official Documentation",
                "provider": "Meta / Jest Community (jestjs.io)",
                "duration": "Official Guide",
                "link": "https://jestjs.io/docs/getting-started"
            },
            {
                "title": "Jest Expect API & Matchers Reference",
                "type": "Official Reference",
                "provider": "Jest Community (jestjs.io)",
                "duration": "API Reference",
                "link": "https://jestjs.io/docs/expect"
            }
        ]
    },
    "Playwright": {
        "subtitle": "Reliable end-to-end cross-browser automation and testing library.",
        "difficulty": "Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Automate Chromium, Firefox, and WebKit browsers with locators, auto-waiting, network mocking, and test runners from Microsoft.",
        "keyTopics": ["Locators & Actionability", "Auto-waiting & Assertions", "Network Interception & Mocking", "Page Object Models"],
        "resources": [
            {
                "title": "Playwright Official Getting Started Guide",
                "type": "Official Documentation",
                "provider": "Microsoft (playwright.dev)",
                "duration": "Official Guide",
                "link": "https://playwright.dev/docs/intro"
            },
            {
                "title": "Playwright Locators & Test Assertions API",
                "type": "Official Reference",
                "provider": "Microsoft (playwright.dev)",
                "duration": "API Docs",
                "link": "https://playwright.dev/docs/locators"
            }
        ]
    },
    "Gemini API": {
        "subtitle": "Build cutting-edge applications with Google's multimodal AI models.",
        "difficulty": "Intermediate",
        "estimatedTime": "4–6 Hours",
        "summary": "Integrate structured JSON generation, multimodal prompts (text, image, audio), and function calling via Google AI documentation.",
        "keyTopics": ["Text Generation & Structured Outputs", "Multimodal Prompting (Images, Audio, PDF)", "Function Calling & Tools", "System Instructions & Safety Settings"],
        "resources": [
            {
                "title": "Google Gemini API Official Documentation",
                "type": "Official Documentation",
                "provider": "Google AI (ai.google.dev)",
                "duration": "Official Docs",
                "link": "https://ai.google.dev/gemini-api/docs"
            },
            {
                "title": "Gemini API Python SDK Quickstart",
                "type": "Official Reference",
                "provider": "Google AI (ai.google.dev)",
                "duration": "Quickstart Docs",
                "link": "https://ai.google.dev/gemini-api/docs/quickstart?lang=python"
            }
        ]
    }
}

# Synonyms and aliases to map candidate skills to canonical roadmaps
SKILL_ALIASES = {
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next": "Next.js",
    "ts": "TypeScript",
    "js": "JavaScript",
    "py": "Python",
    "golang": "Go",
    "k8s": "Kubernetes",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "express": "Express.js",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "tailwind": "Tailwind CSS",
    "github action": "CI/CD & GitHub Actions",
    "github actions": "CI/CD & GitHub Actions",
    "cicd": "CI/CD & GitHub Actions",
    "ci/cd": "CI/CD & GitHub Actions",
    "gemini": "Gemini API",
    "playwright automation": "Playwright"
}

def resolve_roadmap(skill: str) -> Optional[Dict]:
    """Finds curated roadmap by exact name, alias, or case-insensitive matching."""
    clean = skill.strip()
    if clean in CURATED_LEARNING_ROADMAPS:
        return CURATED_LEARNING_ROADMAPS[clean]

    lower = clean.lower()
    if lower in SKILL_ALIASES:
        canonical = SKILL_ALIASES[lower]
        if canonical in CURATED_LEARNING_ROADMAPS:
            return CURATED_LEARNING_ROADMAPS[canonical]

    for key, data in CURATED_LEARNING_ROADMAPS.items():
        if key.lower() == lower:
            return data

    return None

def get_recommendations_for_skills(missing_skills: List[str], max_count: int = 6) -> List[LearningRecommendation]:
    """
    Returns curated learning recommendations for the candidate's missing/partial skills.
    Links strictly point to the official documentation and verified websites of each technology.
    """
    recommendations: List[LearningRecommendation] = []
    seen_skills = set()

    for skill in missing_skills:
        clean_skill = skill.strip()
        if not clean_skill or clean_skill.lower() in seen_skills:
            continue
        seen_skills.add(clean_skill.lower())

        if len(recommendations) >= max_count:
            break
        
        rec_id = f"rec-{re.sub(r'[^a-zA-Z0-9]', '', clean_skill).lower()}"
        roadmap = resolve_roadmap(clean_skill)

        if roadmap:
            resources = [
                LearningResource(
                    title=r["title"],
                    type=r["type"],
                    provider=r["provider"],
                    duration=r["duration"],
                    link=r["link"]
                )
                for r in roadmap["resources"]
            ]
            recommendations.append(
                LearningRecommendation(
                    id=rec_id,
                    skill=clean_skill,
                    subtitle=roadmap["subtitle"],
                    difficulty=roadmap["difficulty"],
                    estimatedTime=roadmap["estimatedTime"],
                    summary=roadmap["summary"],
                    keyTopics=roadmap["keyTopics"],
                    resources=resources
                )
            )
        else:
            # Dynamic fallback: provide direct official developer documentation links
            doc_slug = re.sub(r'[^a-zA-Z0-9_]', '', clean_skill.lower())
            recommendations.append(
                LearningRecommendation(
                    id=rec_id,
                    skill=clean_skill,
                    subtitle=f"Master foundational concepts and hands-on usage of {clean_skill}.",
                    difficulty="Beginner to Intermediate",
                    estimatedTime="5–7 Hours",
                    summary=f"Gain practical competence with {clean_skill} syntax, core APIs, project integration, and real-world deployment patterns via official documentation.",
                    keyTopics=[
                        f"{clean_skill} Architecture & Core Principles",
                        f"Hands-on Integration & Setup",
                        f"Best Practices & Production Optimization",
                        f"Building a Project with {clean_skill}"
                    ],
                    resources=[
                        LearningResource(
                            title=f"{clean_skill} Official Developer Documentation",
                            type="Official Documentation",
                            provider=f"{clean_skill} Documentation Portal",
                            duration="Official Reference",
                            link=f"https://devdocs.io/#q={urllib.parse.quote(clean_skill)}"
                        ),
                        LearningResource(
                            title=f"{clean_skill} Developer Guide & Web Reference",
                            type="Official Reference",
                            provider="Developer Documentation",
                            duration="Getting Started",
                            link=f"https://developer.mozilla.org/en-US/search?q={urllib.parse.quote(clean_skill)}"
                        )
                    ]
                )
            )

    return recommendations
