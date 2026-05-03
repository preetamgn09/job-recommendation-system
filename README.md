<p align="center">
  <h1 align="center">🚀 JobFlow AI</h1>
  <p align="center">
    <strong>Distributed Job Recommendation System</strong>
    <br />
    A scalable, microservices-based backend that stores user profiles, tracks behavior, and recommends jobs in real-time — built like LinkedIn Jobs / Indeed / Naukri.com
    <br /><br />
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
    <img src="https://img.shields.io/badge/MongoDB-7.0-47A248?logo=mongodb&logoColor=white" />
    <img src="https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis&logoColor=white" />
    <img src="https://img.shields.io/badge/RabbitMQ-3.13-FF6600?logo=rabbitmq&logoColor=white" />
    <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" />
    <img src="https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikitlearn&logoColor=white" />
    <br /><br />
    <a href="https://render.com/deploy?repo=https://github.com/preetamgn09/job-recommendation-system"><img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" /></a>
  </p>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started (Local)](#-getting-started-local)
- [Cloud Deployment (Render)](#-cloud-deployment-render)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**JobFlow AI** is a production-ready distributed job recommendation system built with a microservices architecture. It demonstrates real-world patterns used by companies like LinkedIn, Indeed, and Naukri.com for recommending jobs to users based on their skills, preferences, and activity history.

### Key Features

- 🧠 **Smart Recommendations** — TF-IDF vectorization + cosine similarity with activity-based boosting
- ⚡ **Real-Time Event Processing** — RabbitMQ-powered async event pipeline
- 🔄 **Auto-Invalidating Cache** — Redis caching with smart TTL and event-driven invalidation
- 🏗️ **True Microservices** — 5 independent services communicating via HTTP + message queues
- 📊 **50 Realistic Job Listings** — Pre-seeded data spanning 10+ job categories
- 🖥️ **Premium Dashboard** — Dark-mode glassmorphism UI with real-time interactions

---

## 🏗️ Architecture

```
                    ┌──────────────────────────────────────────────────┐
                    │                   Client (Browser)               │
                    └──────────────────────┬───────────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────────┐
                    │              🚪 API Gateway (:8000)              │
                    │         FastAPI + httpx Reverse Proxy             │
                    │         Serves Frontend Dashboard                 │
                    └──────┬──────────┬──────────┬─────────────────────┘
                           │          │          │
              ┌────────────┘          │          └────────────┐
              ▼                       ▼                       ▼
   ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
   │ 👤 User Service   │  │ 💼 Job Service    │  │ 🧠 Recommendation │
   │    (:8001)        │  │    (:8002)        │  │   Service (:8003) │
   │                   │  │                   │  │                   │
   │ • User CRUD       │  │ • Job CRUD        │  │ • TF-IDF Engine   │
   │ • Skill Profiles  │  │ • Text Search     │  │ • Cosine Similarity│
   │ • Activity Log    │  │ • 50 Seed Jobs    │  │ • Activity Boost  │
   └───────┬───────────┘  └───────┬───────────┘  └───────┬───────────┘
           │                      │                       │
           └──────────┬───────────┘                       │
                      ▼                                   │
           ┌────────────────────┐                         │
           │  🗄️ MongoDB (:27017)│◄────────────────────────┘
           └────────────────────┘
                                          ┌────────────────────┐
           ┌────────────────────┐         │  ⚡ Redis (:6379)   │
           │ 🐰 RabbitMQ       │         │  Recommendation     │
           │   (:5672/:15672)  │         │  Cache (5 min TTL)  │
           └────────┬───────────┘         └────────────────────┘
                    │
                    ▼
           ┌────────────────────┐
           │ 📡 Event Service   │
           │                    │
           │ • Process Clicks   │
           │ • Track Applies    │
           │ • Invalidate Cache │
           │ • Update Profiles  │
           └────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | FastAPI 0.115 | Async REST APIs with auto-generated docs |
| **Database** | MongoDB 7.0 (Motor) | Async document storage for users & jobs |
| **Cache** | Redis 7.0 | Recommendation caching with TTL |
| **Message Queue** | RabbitMQ 3.13 | Async event-driven communication |
| **ML Engine** | scikit-learn 1.5 | TF-IDF vectorization + cosine similarity |
| **HTTP Client** | httpx | Async inter-service communication |
| **Containerization** | Docker Compose | Multi-container orchestration |
| **Frontend** | Vanilla HTML/CSS/JS | Premium dark-mode dashboard |

---

## 📁 Project Structure

```
job-recommendation-system/
│
├── docker-compose.yml          # 8 containers orchestration
├── render.yaml                 # Render.com deployment blueprint
├── .env                        # Environment configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── common/                     # Shared utilities across services
│   ├── __init__.py
│   ├── events.py               # Event types + serialization
│   ├── metrics.py              # Response time tracking
│   └── logging_config.py       # Structured JSON logging
│
├── api-gateway/                # 🚪 Entry point — reverse proxy
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app + route proxying
│       ├── config.py           # Service URLs configuration
│       ├── proxy.py            # Generic async reverse proxy
│       ├── middleware.py       # Request logging middleware
│       ├── events.py           # RabbitMQ event publisher
│       └── static/
│           ├── index.html      # Dashboard HTML
│           ├── style.css       # Premium design system
│           └── app.js          # Frontend logic
│
├── user-service/               # 👤 User management
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── config.py           # Service configuration
│       ├── database.py         # MongoDB connection (Motor)
│       ├── schemas.py          # Pydantic request/response models
│       ├── service.py          # Business logic layer
│       └── routes.py           # REST API endpoints
│
├── job-service/                # 💼 Job listings
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── config.py           # Service configuration
│       ├── database.py         # MongoDB + text search index
│       ├── schemas.py          # Pydantic models
│       ├── service.py          # Business logic + search
│       ├── routes.py           # REST API endpoints
│       └── seed.py             # 50 realistic job listings
│
├── recommendation-service/     # 🧠 ML-powered recommendations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── config.py           # Engine tuning parameters
│       ├── database.py         # MongoDB connection
│       ├── engine.py           # ⭐ TF-IDF + cosine similarity
│       ├── cache.py            # Redis caching layer
│       ├── service.py          # Orchestration logic
│       └── routes.py           # REST API endpoints
│
├── event-service/              # 📡 Async event processing
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # RabbitMQ consumer main loop
│       ├── config.py           # Service configuration
│       ├── database.py         # MongoDB connection
│       ├── publisher.py        # Event publisher
│       └── consumers.py        # Event handlers
│
└── seed-users/                 # 🌱 Sample data (optional)
    └── sample_users.json       # 20 pre-built user profiles
```

---

## 🚀 Getting Started (Local)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v4.x+)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/preetamgn09/job-recommendation-system.git
cd job-recommendation-system
```

### 2. Launch Everything (One Command!)

```bash
docker-compose up --build
```

> ⏳ First run takes ~3-5 minutes (downloading MongoDB, Redis, RabbitMQ images + building Python containers)

### 3. Access the Application

| Service | URL |
|---------|-----|
| 🖥️ **Dashboard** | http://localhost:8000 |
| 📖 User Service Docs | http://localhost:8001/docs |
| 📖 Job Service Docs | http://localhost:8002/docs |
| 📖 Recommendation Docs | http://localhost:8003/docs |
| 🐰 RabbitMQ Management | http://localhost:15672 (guest/guest) |

### 4. Quick Demo Flow

1. Open http://localhost:8000
2. Register with skills (e.g., `python, machine learning, sql`)
3. Jobs are auto-seeded (50 realistic listings)
4. View personalized recommendations
5. Click/Apply to jobs → watch recommendations update in real-time!

### Stop Everything

```bash
docker-compose down          # Stop containers
docker-compose down -v       # Stop + delete data volumes
```

---

## ☁️ Cloud Deployment (Render)

Deploy the entire system to the cloud for a **real public URL** — 100% free!

### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/preetamgn09/job-recommendation-system)

### Manual Deployment

#### Step 1: Set Up Free Managed Services

| Service | Provider | Free Tier | Sign Up |
|---------|----------|-----------|--------|
| 🗄️ MongoDB | MongoDB Atlas | 512 MB | [mongodb.com/atlas](https://www.mongodb.com/atlas) |
| ⚡ Redis | Redis Cloud | 30 MB | [redis.io/cloud](https://redis.io/cloud/) |
| 🐰 RabbitMQ | CloudAMQP | 1M msgs/mo | [cloudamqp.com](https://www.cloudamqp.com/) |

#### Step 2: Deploy on Render.com

1. Sign up at [render.com](https://render.com) with your GitHub account
2. For each service, click **"New" → "Web Service"** → Connect `preetamgn09/job-recommendation-system`
3. Configure:

| Render Service | Dockerfile Path | Type |
|---------------|----------------|------|
| `jobflow-user-service` | `user-service/Dockerfile` | Web Service |
| `jobflow-job-service` | `job-service/Dockerfile` | Web Service |
| `jobflow-recommendation-service` | `recommendation-service/Dockerfile` | Web Service |
| `jobflow-api-gateway` | `api-gateway/Dockerfile` | Web Service |
| `jobflow-event-service` | `event-service/Dockerfile` | Background Worker |

> **Important**: Set the **Root Directory** to `.` (repo root) for all services.

#### Step 3: Add Environment Variables

For **all services**, add:
```
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/job_recommendation
MONGO_DB=job_recommendation
REDIS_URL=redis://default:pass@host:port
RABBITMQ_URL=amqps://user:pass@host/vhost
```

For **API Gateway**, also add:
```
USER_SERVICE_URL=https://jobflow-user-service.onrender.com
JOB_SERVICE_URL=https://jobflow-job-service.onrender.com
RECOMMENDATION_SERVICE_URL=https://jobflow-recommendation-service.onrender.com
```

For **Recommendation Service**, also add:
```
USER_SERVICE_URL=https://jobflow-user-service.onrender.com
JOB_SERVICE_URL=https://jobflow-job-service.onrender.com
```

For **Event Service**, also add:
```
RECOMMENDATION_SERVICE_URL=https://jobflow-recommendation-service.onrender.com
```

#### Step 4: Access Your Live App

Your app will be live at:
```
https://jobflow-api-gateway.onrender.com
```

> ⚠️ **Note**: Render's free tier sleeps after 15 min of inactivity. First request after idle takes ~30s.

---

## 📡 API Reference

### User Service (`:8001`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/register` | Create a new user profile |
| `GET` | `/users/{id}` | Get user by ID |
| `PUT` | `/users/{id}` | Update user profile |
| `DELETE` | `/users/{id}` | Delete user |
| `GET` | `/users/` | List all users (paginated) |
| `POST` | `/users/{id}/activity` | Log user activity |
| `GET` | `/users/{id}/activity` | Get activity history |

### Job Service (`:8002`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/jobs/` | Create a job listing |
| `GET` | `/jobs/{id}` | Get job by ID |
| `GET` | `/jobs/` | List jobs (paginated) |
| `GET` | `/jobs/search?q=python` | Full-text job search |
| `POST` | `/jobs/seed` | Seed 50 sample jobs |
| `DELETE` | `/jobs/{id}` | Delete a job |

### Recommendation Service (`:8003`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/recommendations/{user_id}` | Get personalized job recommendations |
| `GET` | `/recommendations/{user_id}/explain` | Get recommendations with match reasons |
| `POST` | `/recommendations/invalidate/{user_id}` | Invalidate cached recommendations |
| `POST` | `/recommendations/invalidate-all` | Clear entire recommendation cache |

### API Gateway (`:8000`)

All of the above endpoints are accessible via the gateway with `/api` prefix:
```
POST /api/users/register
GET  /api/jobs/search?q=python
GET  /api/recommendations/{user_id}
POST /api/events/publish
```

---

## 🧠 How It Works

### Recommendation Engine

The recommendation engine uses a **hybrid approach**:

```
Final Score = (0.7 × Content Score) + (0.3 × Activity Score)
```

**1. Content-Based Filtering (TF-IDF)**
- User profile text = `skills + preferred_roles + location`
- Job text = `title + required_skills + description + category`
- Both are vectorized using TF-IDF, then compared using cosine similarity

**2. Activity-Based Boosting**
- Past clicks and applications are tracked
- Jobs in similar categories get a boost based on historical behavior

**3. Match Reasons**
- Each recommendation includes human-readable explanations
- Example: *"Strong skill match: python, ml"* or *"Based on your interest in Data Science roles"*

### Event Flow

```
User clicks job → API Gateway publishes event to RabbitMQ
                      ↓
              Event Service consumes event
                      ↓
              Updates user's activity in MongoDB
                      ↓
              Invalidates Redis recommendation cache
                      ↓
              Next recommendation request → fresh results
```

---

## 🖥️ Screenshots

> The premium dashboard features a dark-mode glassmorphism design with real-time interactions.

- **Hero Section** — Animated gradient background with system overview
- **User Profile** — Register/login with skills and preferences
- **Job Browser** — Search and filter 50+ job listings
- **Recommendations** — AI-powered personalized job matches with match scores
- **System Monitor** — Live architecture diagram with service health status

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ⭐ Star This Repo!

If you found this project useful or learned something from it, please give it a star! ⭐

---

<p align="center">
  Built with ❤️ using FastAPI, MongoDB, Redis, RabbitMQ & scikit-learn
</p>
