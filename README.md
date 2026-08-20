# Docker_FastAPI_Vue_Calculator

![Project Logo](images/image.png)

# Full-stack calculator web application built with **Vue 3 (Vite)**, **Flask (Python REST API)**, and **MongoDB**, fully containerized using **Docker Compose**.

## Tech Stack

- **Frontend:** Vue 3 (Composition API), Vite, NGINX (Multi-stage Docker build)
- **Backend:** Flask, Gunicorn, PyMongo
- **Database:** MongoDB 6.0 (Persistent volume storage)
- **Orchestration:** Docker Compose

## Project Structure
    calculator-app/
    ├── docker-compose.yml
    ├── backend/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app.py
    └── frontend/
        ├── Dockerfile
        ├── index.html
        ├── style.css
        └── app.js

# How to Run
    Open terminal and run

    docker compose up --build

    # Open browser

    Open your browser:
        Frontend UI: http://localhost:3000
        Backend API: http://localhost:5000/api/history
        MongoDB: Available on localhost:27017

# Features
    Persistent Calculations: History survives container restarts via named Docker volumes.


# Useful Docker Commands

    # View live container logs
    docker compose logs -f

    # View backend logs specifically
    docker logs -f calc_backend

    # Stop all running services
    docker compose down

    # Stop and wipe database volume
    docker compose down -v

    # Rebuild a single service after code changes
    docker compose up -d --build backend

