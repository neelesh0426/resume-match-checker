import re
from typing import Any, Dict, List, Set, Tuple, Optional
from rapidfuzz import fuzz
from app.services.model_loader import get_spacy_nlp
from spacy.matcher import PhraseMatcher

# Comprehensive, categorized skills taxonomy
SKILLS_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # Languages & Runtimes
    "JavaScript": {"category": "Languages", "aliases": ["js", "es6", "vanilla js", "ecmascript"]},
    "TypeScript": {"category": "Languages", "aliases": ["ts"]},
    "Python": {"category": "Languages", "aliases": ["py", "python3"]},
    "Java": {"category": "Languages", "aliases": ["core java", "j2ee"]},
    "C++": {"category": "Languages", "aliases": ["cpp", "c plus plus"]},
    "C#": {"category": "Languages", "aliases": ["csharp", "c sharp", ".net c#"]},
    "Go": {"category": "Languages", "aliases": ["golang"]},
    "Rust": {"category": "Languages", "aliases": []},
    "PHP": {"category": "Languages", "aliases": ["php8", "php7"]},
    "Ruby": {"category": "Languages", "aliases": ["ruby on rails"]},
    "Swift": {"category": "Languages", "aliases": []},
    "Kotlin": {"category": "Languages", "aliases": []},
    "SQL": {"category": "Languages", "aliases": ["structured query language", "t-sql", "pl/sql"]},
    "HTML/CSS": {"category": "Languages", "aliases": ["html", "html5", "css", "css3"]},
    "R": {"category": "Languages", "aliases": ["r language"]},

    # Frontend Frameworks & Libraries
    "React": {"category": "Frontend", "aliases": ["reactjs", "react.js", "react native"]},
    "Angular": {"category": "Frontend", "aliases": ["angularjs", "angular 2+"]},
    "Vue.js": {"category": "Frontend", "aliases": ["vue", "vuejs", "vue3"]},
    "Next.js": {"category": "Frontend", "aliases": ["nextjs"]},
    "Svelte": {"category": "Frontend", "aliases": ["sveltekit"]},
    "Tailwind CSS": {"category": "Frontend", "aliases": ["tailwind", "tailwindcss"]},
    "Redux": {"category": "Frontend", "aliases": ["redux toolkit", "rtk"]},
    "Webpack": {"category": "Frontend", "aliases": ["vite", "rollup", "turbopack"]},

    # Backend & APIs
    "Node.js": {"category": "Backend", "aliases": ["node", "nodejs"]},
    "FastAPI": {"category": "Backend", "aliases": ["fast api"]},
    "Express.js": {"category": "Backend", "aliases": ["express", "expressjs"]},
    "Django": {"category": "Backend", "aliases": ["django rest framework", "drf"]},
    "Flask": {"category": "Backend", "aliases": []},
    "Spring Boot": {"category": "Backend", "aliases": ["spring", "spring framework", "spring cloud"]},
    ".NET Core": {"category": "Backend", "aliases": [".net", "asp.net", "asp.net core", "dotnet"]},
    "REST APIs": {"category": "Backend", "aliases": ["rest", "restful", "restful api", "restful apis", "web api"]},
    "GraphQL": {"category": "Backend", "aliases": ["apollo graphql"]},
    "Microservices": {"category": "Backend", "aliases": ["microservice architecture", "micro-services"]},
    "gRPC": {"category": "Backend", "aliases": ["protobuf", "protocol buffers"]},

    # Databases & Storage
    "PostgreSQL": {"category": "Databases", "aliases": ["postgres", "pgsql", "psql"]},
    "MySQL": {"category": "Databases", "aliases": ["mariadb"]},
    "MongoDB": {"category": "Databases", "aliases": ["mongo"]},
    "Redis": {"category": "Databases", "aliases": ["redis cache"]},
    "SQLite": {"category": "Databases", "aliases": []},
    "Elasticsearch": {"category": "Databases", "aliases": ["elastic", "elk stack", "opensearch"]},
    "DynamoDB": {"category": "Databases", "aliases": ["amazon dynamodb"]},
    "Cassandra": {"category": "Databases", "aliases": ["apache cassandra"]},
    "Oracle Database": {"category": "Databases", "aliases": ["oracle db", "oracle sql"]},
    "Firebase": {"category": "Databases", "aliases": ["firestore", "firebase realtime database"]},

    # Cloud & DevOps
    "Amazon Web Services": {"category": "Cloud & DevOps", "aliases": ["aws", "amazon cloud", "ec2", "s3", "lambda"]},
    "Google Cloud Platform": {"category": "Cloud & DevOps", "aliases": ["gcp", "google cloud"]},
    "Microsoft Azure": {"category": "Cloud & DevOps", "aliases": ["azure", "azure cloud"]},
    "Docker": {"category": "Cloud & DevOps", "aliases": ["docker compose", "containerization", "containers"]},
    "Kubernetes": {"category": "Cloud & DevOps", "aliases": ["k8s", "kubectl", "helm"]},
    "CI/CD": {"category": "Cloud & DevOps", "aliases": ["continuous integration", "continuous deployment", "ci cd", "cicd"]},
    "GitHub Actions": {"category": "Cloud & DevOps", "aliases": ["github action", "gh actions"]},
    "GitLab CI": {"category": "Cloud & DevOps", "aliases": ["gitlab ci/cd"]},
    "Jenkins": {"category": "Cloud & DevOps", "aliases": []},
    "Terraform": {"category": "Cloud & DevOps", "aliases": ["iac", "infrastructure as code"]},
    "Linux": {"category": "Cloud & DevOps", "aliases": ["unix", "bash", "shell scripting"]},
    "Nginx": {"category": "Cloud & DevOps", "aliases": ["reverse proxy"]},

    # AI, Machine Learning & Data
    "Machine Learning": {"category": "AI & Data", "aliases": ["ml", "supervised learning", "unsupervised learning"]},
    "Deep Learning": {"category": "AI & Data", "aliases": ["dl", "neural networks", "cnn", "rnn", "lstm"]},
    "Artificial Intelligence": {"category": "AI & Data", "aliases": ["ai", "genai", "generative ai"]},
    "PyTorch": {"category": "AI & Data", "aliases": ["torch"]},
    "TensorFlow": {"category": "AI & Data", "aliases": ["tf", "keras"]},
    "Scikit-learn": {"category": "AI & Data", "aliases": ["sklearn"]},
    "Pandas": {"category": "AI & Data", "aliases": []},
    "NumPy": {"category": "AI & Data", "aliases": []},
    "Natural Language Processing": {"category": "AI & Data", "aliases": ["nlp", "spacy", "nltk", "transformers"]},
    "Large Language Models": {"category": "AI & Data", "aliases": ["llm", "llms", "rag", "langchain", "llama"]},
    "Computer Vision": {"category": "AI & Data", "aliases": ["cv", "opencv"]},
    "BigQuery": {"category": "AI & Data", "aliases": ["google bigquery"]},
    "Apache Spark": {"category": "AI & Data", "aliases": ["spark", "pyspark"]},
    "Apache Kafka": {"category": "AI & Data", "aliases": ["kafka"]},

    # Architecture, Testing & Methodologies
    "System Design": {"category": "Architecture", "aliases": ["software architecture", "high-level design", "hld", "lld"]},
    "Unit Testing": {"category": "Testing", "aliases": ["jest", "pytest", "mocha", "junit", "tdd", "test-driven development"]},
    "Integration Testing": {"category": "Testing", "aliases": ["e2e testing", "cypress", "playwright", "selenium"]},
    "Git": {"category": "Tools", "aliases": ["git version control", "github", "gitlab", "bitbucket"]},
    "Agile": {"category": "Methodology", "aliases": ["scrum", "kanban", "sprints"]},
    "Problem Solving": {"category": "Soft Skills", "aliases": ["analytical skills", "critical thinking"]},
    "Communication": {"category": "Soft Skills", "aliases": ["verbal communication", "written communication", "presentation skills"]},
    "Leadership": {"category": "Soft Skills", "aliases": ["mentoring", "team lead", "cross-functional collaboration"]},
    "Project Management": {"category": "Methodology", "aliases": ["jira", "confluence", "trello"]}
}

# Inverted mapping: token/alias (lowercase) -> canonical skill name
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, data in SKILLS_TAXONOMY.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in data.get("aliases", []):
        ALIAS_TO_CANONICAL[alias.lower()] = canonical

_phrase_matcher: Optional[PhraseMatcher] = None


def get_skill_phrase_matcher() -> PhraseMatcher:
    """Initialize or return cached spaCy PhraseMatcher with all skills and aliases."""
    global _phrase_matcher
    if _phrase_matcher is None:
        nlp = get_spacy_nlp()
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        for alias_phrase, canonical in ALIAS_TO_CANONICAL.items():
            # Skip single-character aliases to avoid false positive explosions
            if len(alias_phrase) < 2:
                continue
            doc = nlp.make_doc(alias_phrase)
            matcher.add(canonical, [doc])
        _phrase_matcher = matcher
    return _phrase_matcher


def extract_skills_from_text(text: str) -> Dict[str, Dict[str, any]]:
    """Extract skills from text using spaCy PhraseMatcher and RapidFuzz regex boundary validation.
    Returns {canonical_skill_name: {"category": str, "matched_via": Optional[str]}}
    """
    if not text:
        return {}

    nlp = get_spacy_nlp()
    doc = nlp(text.lower())
    matcher = get_skill_phrase_matcher()
    matches = matcher(doc)

    found_skills: Dict[str, Dict[str, any]] = {}

    for match_id, start, end in matches:
        canonical = nlp.vocab.strings[match_id]
        span_text = doc[start:end].text.strip()
        category = SKILLS_TAXONOMY.get(canonical, {}).get("category", "General")

        matched_via = span_text if span_text.lower() != canonical.lower() else None
        if canonical not in found_skills:
            found_skills[canonical] = {
                "name": canonical,
                "category": category,
                "matched_via": matched_via
            }

    # Second pass: Exact regex boundary check for short aliases like 'C++', 'C#', 'R', 'Go', 'AWS', 'GCP', 'K8s', 'JS', 'TS'
    # which spaCy tokenizers sometimes partition or miss
    short_patterns = [
        (r"\bjs\b", "JavaScript", "js"),
        (r"\bts\b", "TypeScript", "ts"),
        (r"\bpostgres\b", "PostgreSQL", "postgres"),
        (r"\bpgsql\b", "PostgreSQL", "pgsql"),
        (r"\baws\b", "Amazon Web Services", "aws"),
        (r"\bgcp\b", "Google Cloud Platform", "gcp"),
        (r"\bk8s\b", "Kubernetes", "k8s"),
        (r"\bc\+\+\b", "C++", "c++"),
        (r"\bc#\b", "C#", "c#"),
        (r"\bci\/cd\b", "CI/CD", "ci/cd"),
        (r"\bnode(?:\.js)?\b", "Node.js", "node"),
        (r"\breact(?:\.js)?\b", "React", "react"),
        (r"\bvue(?:\.js)?\b", "Vue.js", "vue"),
        (r"\bml\b", "Machine Learning", "ml"),
        (r"\bdl\b", "Deep Learning", "dl"),
        (r"\bai\b", "Artificial Intelligence", "ai"),
        (r"\bllms?\b", "Large Language Models", "llm"),
        (r"\bnlp\b", "Natural Language Processing", "nlp"),
        (r"\btf\b", "TensorFlow", "tf"),
        (r"\bsklearn\b", "Scikit-learn", "sklearn"),
        (r"\bmongo\b", "MongoDB", "mongo"),
        (r"\belastic\b", "Elasticsearch", "elastic"),
    ]

    lower_text = text.lower()
    for pattern, canonical, alias in short_patterns:
        if canonical not in found_skills:
            if re.search(pattern, lower_text):
                found_skills[canonical] = {
                    "name": canonical,
                    "category": SKILLS_TAXONOMY.get(canonical, {}).get("category", "General"),
                    "matched_via": alias
                }

    # RapidFuzz fallback for multi-word skill aliases with slight misspellings (threshold >= 92)
    # Only checks words if skill not found yet
    words = set(re.findall(r"[a-z0-9\-\+\#]+", lower_text))
    for canonical, data in SKILLS_TAXONOMY.items():
        if canonical not in found_skills:
            # Check canonical name fuzzy match against phrases
            c_lower = canonical.lower()
            if " " not in c_lower and len(c_lower) > 4:
                for w in words:
                    if len(w) >= len(c_lower) - 1 and fuzz.ratio(c_lower, w) >= 92:
                        found_skills[canonical] = {
                            "name": canonical,
                            "category": data.get("category", "General"),
                            "matched_via": f"{w} (approx)"
                        }
                        break

    return found_skills


def segment_job_description(jd_text: str) -> Tuple[str, str, str]:
    """Segment a job description into (required_section, preferred_section, general_section)."""
    required_keywords = [
        "requirements", "required qualifications", "minimum qualifications", "must have",
        "what you'll need", "what you need", "what you bring", "qualifications", "core requirements",
        "basic qualifications", "essential requirements", "must-have", "minimum requirements"
    ]
    preferred_keywords = [
        "preferred qualifications", "nice to have", "bonus", "bonus points", "good to have",
        "preferred skills", "desired qualifications", "plus", "what gives you an edge",
        "additional qualifications", "preferred", "nice-to-have"
    ]

    lines = jd_text.split("\n")
    required_lines = []
    preferred_lines = []
    general_lines = []

    current_section = "general"

    for line in lines:
        stripped = line.strip()
        clean_lower = re.sub(r"[^a-z0-9\s]", "", stripped.lower()).strip()

        # Check if line looks like a header
        is_header = len(stripped) < 60 and (
            stripped.endswith(":") or line.isupper() or stripped.startswith(("#", "*", "-"))
        )

        matched_req = any(kw in clean_lower for kw in required_keywords)
        matched_pref = any(kw in clean_lower for kw in preferred_keywords)

        if matched_pref:
            current_section = "preferred"
            preferred_lines.append(line)
        elif matched_req:
            current_section = "required"
            required_lines.append(line)
        elif is_header and ("responsibilities" in clean_lower or "about" in clean_lower or "benefits" in clean_lower):
            current_section = "general"
            general_lines.append(line)
        else:
            if current_section == "required":
                required_lines.append(line)
            elif current_section == "preferred":
                preferred_lines.append(line)
            else:
                general_lines.append(line)

    return (
        "\n".join(required_lines).strip(),
        "\n".join(preferred_lines).strip(),
        "\n".join(general_lines).strip()
    )


def extract_jd_skills(jd_text: str) -> Tuple[Dict[str, Dict[str, any]], Dict[str, Dict[str, any]]]:
    """Extract required and preferred skills from the job description.
    Returns (required_skills_dict, preferred_skills_dict).
    """
    req_text, pref_text, gen_text = segment_job_description(jd_text)

    req_skills = extract_skills_from_text(req_text)
    pref_skills = extract_skills_from_text(pref_text)

    # If general section exists, check sentence context for requirement indicators
    if gen_text:
        gen_skills = extract_skills_from_text(gen_text)
        lower_gen = gen_text.lower()
        for skill_name, skill_info in gen_skills.items():
            if skill_name in req_skills or skill_name in pref_skills:
                continue

            # Check if skill sentence has requirement verbs
            # E.g. "Must have experience with Docker" vs "Familiarity with Kubernetes is a plus"
            sentences = re.split(r"[.!?\n]", lower_gen)
            is_req = False
            is_pref = False
            for s in sentences:
                if skill_name.lower() in s or (skill_info.get("matched_via") and skill_info["matched_via"] in s):
                    if any(w in s for w in ["must", "required", "minimum", "at least", "essential", "have to"]):
                        is_req = True
                        break
                    elif any(w in s for w in ["nice to have", "plus", "bonus", "preferred", "optional"]):
                        is_pref = True
                        break

            if is_pref:
                pref_skills[skill_name] = skill_info
            elif is_req:
                req_skills[skill_name] = skill_info
            else:
                # Default non-classified skills to required if required set is small, or preferred
                if len(req_skills) < 3:
                    req_skills[skill_name] = skill_info
                else:
                    pref_skills[skill_name] = skill_info

    # If NO required skills were detected at all from headers/context, fall back to entire text
    if not req_skills and not pref_skills:
        all_skills = extract_skills_from_text(jd_text)
        # Allocate top technical skills as required
        for idx, (s_name, s_info) in enumerate(all_skills.items()):
            if idx < max(3, len(all_skills) // 2):
                req_skills[s_name] = s_info
            else:
                pref_skills[s_name] = s_info

    return req_skills, pref_skills
