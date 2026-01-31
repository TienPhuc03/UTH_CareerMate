# CareerMate – Your AI-Powered Job Companion

<div align="center">

![CareerMate Logo](https://img.shields.io/badge/CareerMate-AI--Powered-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**CareerMate** is an AI-powered career companion that helps final-year students and fresh graduates bridge the gap between education and employment through personalized CV optimization, interview coaching, skill roadmaps, and intelligent job matching.

[Features](#features) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [Documentation](#documentation) • [Team](#team)

</div>

---

## 📋 Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [Team](#team)
- [License](#license)

---

## 🎯 About

CareerMate addresses the growing challenges faced by final-year students and fresh graduates in Vietnam's competitive job market. The platform combines AI-driven analysis, personalized career guidance, and intelligent job matching to create an end-to-end career readiness solution.

### 🎯 Vision

To become the leading digital career-readiness platform for students and entry-level candidates in Vietnam, then expand regionally.

### 💡 Why CareerMate?

- **AI-First Design**: Advanced AI capabilities for CV analysis, career coaching, and job matching
- **Personalized Experience**: Tailored recommendations based on individual profiles, skills, and goals
- **End-to-End Support**: From career orientation to job application in one unified platform
- **Student-Focused**: Specifically designed for fresh graduates and entry-level candidates

---

## ✨ Key Features

### For Students/Candidates

- 🤖 **AI CV Analyzer**: Upload your CV and receive instant AI-powered feedback, ATS compatibility scores, and optimization suggestions
- 💬 **AI Career Coach**: Interactive chatbot providing personalized career roadmaps and skill recommendations
- 🎤 **Mock Interview Practice**: AI-driven interview simulations with detailed feedback
- 🔍 **Smart Job Search**: AI-powered job matching based on your skills and preferences
- 📚 **Learning Hub**: Curated courses, articles, and career resources
- 📝 **CV Templates**: Professional ATS-friendly CV templates
- 🏆 **Gamification**: Earn badges and compete on leaderboards through challenges
- 💎 **Premium Services**: Advanced AI analysis and priority job matching

### For Recruiters

- 🏢 **Company Profile Management**: Create and manage your organization's presence
- 📢 **Job Posting**: Post job openings with detailed descriptions
- 👥 **Candidate Pipeline**: Manage recruitment workflow (Shortlist → Interview → Offer)
- 🎯 **AI Matching**: Find the best candidates using AI-powered matching scores
- 🔎 **Smart Search**: Advanced filtering and search capabilities

### For Admins

- 👤 **User Management**: Comprehensive user and role administration
- 📊 **Analytics Dashboard**: Real-time monitoring and reporting
- 📚 **Content Management**: Manage CV templates, interview questions, and resources
- 🔧 **System Monitoring**: Track performance, logs, and AI metrics
- 💳 **Package Management**: Create and manage subscription plans

---

## 🛠 Tech Stack

### Frontend

- **Web Application**: ReactJS with TypeScript, Next.js (optional)
- **Mobile Application**: React Native with TypeScript
- **State Management**: Redux / Zustand / React Query
- **UI Framework**: Tailwind CSS
- **Authentication**: OAuth2 (Google Sign-In)

### Backend

- **Framework**: FastAPI / Django REST Framework (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Vector Database**: Weaviate / Pinecone
- **Object Storage**: AWS S3 / Google Cloud Storage / Azure Blob
- **Authentication**: JWT, OAuth2

### AI & External Services

- **LLM Integration**: OpenAI / Google Gemini
- **Vector Search**: Weaviate / Pinecone Cloud
- **Email Service**: SendGrid
- **Notifications**: Firebase / OneSignal
- **Analytics**: Google Analytics, Sentry
- **Monitoring**: Prometheus / Grafana
- **Payment Gateway**: MoMo, ZaloPay, Stripe (optional)

### DevOps

- **Version Control**: Git, GitHub
- **CI/CD**: GitHub Actions
- **Testing**: Jest (Frontend), JUnit (Backend), Postman/Newman
- **Project Management**: Trello, Jira

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
├──────────────────────┬──────────────────┬───────────────────┤
│   Web Application    │  Mobile App      │  Admin Dashboard  │
│   (React + Next.js)  │  (React Native)  │  (React)          │
└──────────────────────┴──────────────────┴───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway / Backend                    │
│                   (FastAPI / Django REST)                    │
├──────────────────────┬──────────────────┬───────────────────┤
│   Auth Service       │  User Service    │  Job Service      │
│   CV Service         │  AI Orchestrator │  Payment Service  │
└──────────────────────┴──────────────────┴───────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   PostgreSQL     │ │    Redis     │ │   Vector DB      │
│   (Main DB)      │ │   (Cache)    │ │ (Weaviate/Pine)  │
└──────────────────┘ └──────────────┘ └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   AI Services    │ │    Email     │ │  Object Storage  │
│ (OpenAI/Gemini)  │ │  (SendGrid)  │ │   (S3/GCS)       │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: v20.x or higher
- **Python**: v3.9 or higher
- **PostgreSQL**: v13 or higher
- **Redis**: v6 or higher
- **Git**: Latest version
- **Visual Studio Code**: (Recommended IDE)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/TienPhuc03/UTH_CareerMate.git
cd UTH_CareerMate
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python manage.py migrate

# Start the backend server
python manage.py runserver
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

#### 4. Mobile App Setup

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Run on iOS
npm run ios

# Run on Android
npm run android
```

---

## 📖 Usage

### For Students

1. **Sign Up/Login**: Create an account using email or Google OAuth
2. **Build Profile**: Complete your profile with education, skills, and experience
3. **Upload CV**: Upload your CV for AI-powered analysis
4. **Get Feedback**: Receive detailed feedback and improvement suggestions
5. **Career Roadmap**: Consult with AI Career Coach for personalized guidance
6. **Job Search**: Browse and apply for jobs with AI matching scores
7. **Practice Interviews**: Use AI mock interviews to prepare

### For Recruiters

1. **Register Organization**: Create your company profile
2. **Post Jobs**: Add job openings with detailed descriptions
3. **Review Candidates**: Browse AI-matched candidates
4. **Manage Pipeline**: Track candidates through your recruitment workflow
5. **Make Offers**: Send offers to selected candidates

### For Admins

1. **Monitor System**: Track performance and user activities
2. **Manage Users**: Handle user accounts and permissions
3. **Content Management**: Update CV templates and resources
4. **Analytics**: Generate reports and insights

---

## 📁 Project Structure

```
CareerMate/
├── backend/                 # Backend API (Python/FastAPI)
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Helper functions
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Web application (React)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── store/         # State management
│   │   └── utils/         # Utilities
│   └── package.json       # Node dependencies
│
├── mobile/                # Mobile app (React Native)
│   ├── src/
│   │   ├── components/
│   │   ├── screens/
│   │   ├── services/
│   │   └── navigation/
│   └── package.json
│
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── design/           # Design documents
│   └── user-guide/       # User guides
│
└── README.md             # This file
```

---

## 📚 API Documentation

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.careermate.com/api/v1
```

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/google` - Google OAuth login

#### CV Management
- `POST /cv/upload` - Upload CV file
- `GET /cv/analysis/{cv_id}` - Get CV analysis results
- `POST /cv/analyze` - Trigger AI analysis
- `GET /cv/templates` - Get CV templates

#### Job Management
- `GET /jobs` - List all jobs
- `GET /jobs/{job_id}` - Get job details
- `POST /jobs/apply` - Apply for a job
- `GET /jobs/recommendations` - Get AI job recommendations

#### AI Services
- `POST /ai/career-coach` - Chat with AI career coach
- `POST /ai/mock-interview` - Start mock interview
- `GET /ai/roadmap` - Get personalized career roadmap

For complete API documentation, visit `/docs` when running the backend server.

---

## 🧪 Testing

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run with coverage
npm run test:coverage
```

### End-to-End Testing

```bash
# Run E2E tests
npm run test:e2e
```

---

## 📊 Performance Requirements

- **AI Response Time**: ≤ 3.5 seconds
- **API Latency**: ≤ 400ms for standard requests
- **CV Analysis**: < 5 seconds (P95)
- **System Availability**: 99.5% uptime
- **Concurrent Users**: Support 100+ concurrent users (scalable to 1,000+)

---

## 🔒 Security

- **Authentication**: OAuth2, JWT tokens
- **Data Encryption**: At-rest and in-transit encryption
- **HTTPS**: All communications over secure protocols
- **Input Validation**: Comprehensive validation on all inputs
- **RBAC**: Role-based access control for all features
- **Data Privacy**: PDPA and GDPR compliance

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/TypeScript
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- University of Transport Ho Chi Minh City for project support
- OpenAI and Google for AI/LLM services
- All contributors and beta testers

---

## 📞 Contact

For questions or support, please contact:

- **Project Lead**: phucntt0644@ut.edu.vn
- **GitHub Issues**: [Create an issue](https://github.com/TienPhuc03/UTH_CareerMate/issues)

---

<div align="center">

**Made with ❤️ by the CareerMate Team**

⭐ Star us on GitHub — it helps!

[⬆ back to top](#careermate--your-ai-powered-job-companion)

</div>
