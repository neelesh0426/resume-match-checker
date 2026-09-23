import React from 'react';
import { Briefcase, Sparkles } from 'lucide-react';

const SAMPLE_JDS = [
  {
    label: 'Python Backend',
    text: `Senior Python Backend Engineer

About the Role:
We are seeking an experienced Backend Engineer proficient in Python and modern frameworks to design scalable RESTful microservices.

Required Qualifications:
- 3+ years of experience with Python and FastAPI or Django
- Strong SQL proficiency with PostgreSQL, query optimization, and SQLAlchemy
- Deep understanding of REST APIs, Git, and Docker containerization
- Excellent problem-solving, code review, and communication skills

Preferred Qualifications:
- Experience with AWS (ECS, RDS, S3) and Redis caching
- Familiarity with CI/CD pipelines (GitHub Actions)
- Understanding of automated testing with Pytest`,
  },
  {
    label: 'Full Stack Dev',
    text: `Full Stack Software Engineer

Responsibilities:
Build modern end-to-end web applications across our frontend React suite and Node.js microservices.

Requirements:
- 3+ years experience in Full Stack development with TypeScript or JavaScript
- Strong proficiency in React.js, Tailwind CSS, and HTML5/CSS3
- Backend experience in Node.js, Express, and REST APIs
- Familiarity with SQL databases (PostgreSQL or MySQL) and Git version control

Nice to Have:
- Experience with Next.js, GraphQL, and Docker
- Knowledge of cloud platforms like AWS or GCP
- Agile methodologies and team collaboration`,
  },
  {
    label: 'Data / AI Engineer',
    text: `Machine Learning & Data Engineer

Overview:
Looking for a Data & AI Engineer to build scalable machine learning inference pipelines and NLP data processing workflows.

Must Haves:
- Strong programming background in Python, Pandas, and NumPy
- Hands-on experience with Machine Learning models (Scikit-Learn, PyTorch or TensorFlow)
- Experience with Natural Language Processing (NLP), spaCy, and vector embeddings
- Relational databases, SQL, and data transformation pipelines

Bonus Points:
- Hugging Face Transformers and LLM orchestration (LangChain or LlamaIndex)
- FastAPI deployment of ML models
- Cloud deployment on GCP or AWS`,
  }
];

export default function JobDescriptionInput({ jdText, setJdText }) {
  const charCount = jdText.trim().length;
  const isValid = charCount >= 30;

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div className="panel-title-group">
          <div className="panel-icon-wrap">
            <Briefcase size={18} />
          </div>
          <h2 className="panel-title">2. Target Job Description</h2>
        </div>
        <span className="panel-badge">Plain Text</span>
      </div>

      <div className="jd-textarea-wrapper">
        <textarea
          className="jd-textarea"
          placeholder="Paste the target job description here (minimum 30 characters)..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
        />

        <div className="jd-footer">
          <span className={`char-counter ${isValid ? 'valid' : ''}`}>
            {charCount} characters {charCount > 0 && !isValid ? '(min 30)' : ''}
          </span>

          <div className="template-pills">
            <span className="template-label">Sample Templates:</span>
            {SAMPLE_JDS.map((tpl) => (
              <button
                key={tpl.label}
                type="button"
                className="template-btn"
                onClick={() => setJdText(tpl.text)}
              >
                <Sparkles size={11} style={{ marginRight: '3px' }} />
                {tpl.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
