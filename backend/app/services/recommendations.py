from typing import Dict, List, Optional
from app.schemas.analysis import LearningRecommendation, LearningResource

CURATED_LEARNING_ROADMAPS: Dict[str, Dict] = {
    "Docker": {
        "subtitle": "Learn containerization and deployment basics.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Understand container concepts, craft multi-stage Dockerfiles for React single-page apps, and configure local container stacks.",
        "keyTopics": [
            "Dockerfiles & Layers",
            "Containerizing React Vite Apps",
            "Nginx Static Serving",
            "Docker Compose for Multi-Container Stacks"
        ],
        "resources": [
            {
                "title": "Docker for Frontend Developers",
                "type": "Interactive Video",
                "provider": "freeCodeCamp",
                "duration": "2.5 Hours",
                "link": "https://www.freecodecamp.org/news/docker-for-frontend-developers/"
            },
            {
                "title": "Containerize a React App with Nginx",
                "type": "Official Walkthrough",
                "provider": "Docker Documentation",
                "duration": "45 Mins",
                "link": "https://docs.docker.com/guides/language/nodejs/containerize/"
            },
            {
                "title": "Docker Compose for Local Web Stacks",
                "type": "Hands-on Guide",
                "provider": "Web Dev Community",
                "duration": "1.5 Hours",
                "link": "https://docs.docker.com/compose/"
            }
        ]
    },
    "AWS": {
        "subtitle": "Learn core cloud services and deployment.",
        "difficulty": "Intermediate",
        "estimatedTime": "10–12 Hours",
        "summary": "Master deploying web applications to Amazon S3, configuring CloudFront CDN for global caching, and securing routes with IAM.",
        "keyTopics": [
            "Amazon S3 Static Hosting",
            "CloudFront CDN Caching",
            "Route 53 Custom Domains",
            "AWS IAM Security Essentials"
        ],
        "resources": [
            {
                "title": "AWS Cloud Practitioner Essentials",
                "type": "Free Course",
                "provider": "AWS Skill Builder",
                "duration": "6 Hours",
                "link": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials"
            },
            {
                "title": "Deploying Modern React SPAs to S3 + CloudFront",
                "type": "Tutorial",
                "provider": "AWS Community",
                "duration": "1.5 Hours",
                "link": "https://aws.amazon.com/getting-started/hands-on/build-modern-app-fargate-lambda-dynamodb-python/"
            },
            {
                "title": "AWS Lambda & Serverless for Frontends",
                "type": "Practical Lab",
                "provider": "Cloud Guru Labs",
                "duration": "2 Hours",
                "link": "https://aws.amazon.com/serverless/"
            }
        ]
    },
    "System Design": {
        "subtitle": "Learn scalability, APIs and architecture fundamentals.",
        "difficulty": "Intermediate to Advanced",
        "estimatedTime": "8–10 Hours",
        "summary": "Understand client-side state architecture, bundle splitting, CDN caching, rate limiting, and scalable REST API conventions.",
        "keyTopics": [
            "Frontend Performance & Core Web Vitals",
            "Client-Side Caching (SWR / React Query)",
            "Code Splitting & Lazy Loading",
            "RESTful API Conventions & Error Handling"
        ],
        "resources": [
            {
                "title": "Frontend System Design Handbook",
                "type": "Open Source Guide",
                "provider": "GreatFrontEnd",
                "duration": "4 Hours",
                "link": "https://www.greatfrontend.com/system-design"
            },
            {
                "title": "Optimizing Web Vitals for Production",
                "type": "Engineering Guide",
                "provider": "web.dev by Google",
                "duration": "2 Hours",
                "link": "https://web.dev/explore/fast"
            },
            {
                "title": "Designing Resilient API Clients",
                "type": "Deep Dive Article",
                "provider": "Engineering Blog",
                "duration": "1.5 Hours",
                "link": "https://roadmap.sh/software-design-architecture"
            }
        ]
    },
    "Node.js": {
        "subtitle": "Master asynchronous JavaScript server runtimes.",
        "difficulty": "Beginner to Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Build production-grade REST APIs, handle streaming, manage authentication tokens, and connect to SQL/NoSQL databases.",
        "keyTopics": [
            "Event Loop & Async I/O",
            "Express Middleware Architecture",
            "JWT Authentication & Route Guards",
            "Database Connectivity & ORMs"
        ],
        "resources": [
            {
                "title": "Node.js and Express.js Full Course",
                "type": "Video Course",
                "provider": "freeCodeCamp",
                "duration": "8 Hours",
                "link": "https://www.freecodecamp.org/news/free-8-hour-node-js-express-course/"
            },
            {
                "title": "Official Node.js Guides",
                "type": "Documentation",
                "provider": "Node.js Org",
                "duration": "2 Hours",
                "link": "https://nodejs.org/en/learn"
            }
        ]
    },
    "TypeScript": {
        "subtitle": "Level up code reliability with static typing.",
        "difficulty": "Intermediate",
        "estimatedTime": "5–7 Hours",
        "summary": "Transition from plain JavaScript to strict TypeScript with interfaces, generics, utility types, and React prop types.",
        "keyTopics": [
            "Types vs Interfaces",
            "Generic Functions & Components",
            "React.FC and Hook Types",
            "Strict Mode & Tsconfig Tuning"
        ],
        "resources": [
            {
                "title": "TypeScript Handbook",
                "type": "Official Documentation",
                "provider": "Microsoft",
                "duration": "4 Hours",
                "link": "https://www.typescriptlang.org/docs/handbook/intro.html"
            },
            {
                "title": "React with TypeScript CheatSheet",
                "type": "Developer Reference",
                "provider": "GitHub Community",
                "duration": "1 Hour",
                "link": "https://react-typescript-cheatsheet.netlify.app/"
            }
        ]
    },
    "PostgreSQL": {
        "subtitle": "Advanced relational database management.",
        "difficulty": "Intermediate",
        "estimatedTime": "6–8 Hours",
        "summary": "Master relational schema design, indexing, foreign key constraints, JSONB queries, and connection pooling.",
        "keyTopics": [
            "Relational Modeling & Normalization",
            "Indexes (B-Tree, GIN for JSONB)",
            "Complex Joins & Aggregations",
            "Transactions & ACID Principles"
        ],
        "resources": [
            {
                "title": "PostgreSQL Tutorial for Beginners",
                "type": "Interactive Guide",
                "provider": "PostgreSQL Tutorial",
                "duration": "4 Hours",
                "link": "https://www.postgresqltutorial.com/"
            }
        ]
    }
}

def get_recommendations_for_skills(missing_skills: List[str], max_count: int = 3) -> List[LearningRecommendation]:
    """Returns curated learning recommendations for the candidate's missing/partial skills."""
    recommendations: List[LearningRecommendation] = []

    for skill in missing_skills:
        if len(recommendations) >= max_count:
            break
        
        rec_id = f"rec-{skill.lower().replace('.', '').replace(' ', '')}"
        if skill in CURATED_LEARNING_ROADMAPS:
            data = CURATED_LEARNING_ROADMAPS[skill]
            resources = [
                LearningResource(
                    title=r["title"],
                    type=r["type"],
                    provider=r["provider"],
                    duration=r["duration"],
                    link=r["link"]
                )
                for r in data["resources"]
            ]
            recommendations.append(
                LearningRecommendation(
                    id=rec_id,
                    skill=skill,
                    subtitle=data["subtitle"],
                    difficulty=data["difficulty"],
                    estimatedTime=data["estimatedTime"],
                    summary=data["summary"],
                    keyTopics=data["keyTopics"],
                    resources=resources
                )
            )
        else:
            # Fallback dynamic recommendation for any technology
            recommendations.append(
                LearningRecommendation(
                    id=rec_id,
                    skill=skill,
                    subtitle=f"Master foundational concepts and hands-on usage of {skill}.",
                    difficulty="Beginner to Intermediate",
                    estimatedTime="5–7 Hours",
                    summary=f"Gain practical competence with {skill} syntax, core APIs, project integration, and real-world deployment patterns.",
                    keyTopics=[
                        f"{skill} Architecture & Core Principles",
                        f"Hands-on Integration & Setup",
                        f"Best Practices & Production Optimization",
                        f"Building a Portfolio Project with {skill}"
                    ],
                    resources=[
                        LearningResource(
                            title=f"Complete {skill} Developer Guide",
                            type="Tutorial",
                            provider="Developer Community",
                            duration="3 Hours",
                            link=f"https://www.google.com/search?q={skill}+tutorial+freecodecamp"
                        ),
                        LearningResource(
                            title=f"{skill} Official Documentation & Quickstart",
                            type="Official Docs",
                            provider=f"{skill} Community",
                            duration="1.5 Hours",
                            link=f"https://www.google.com/search?q={skill}+official+documentation"
                        )
                    ]
                )
            )

    return recommendations
