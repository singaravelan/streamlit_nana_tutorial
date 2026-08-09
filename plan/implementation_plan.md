# Goal
Create a step-by-step local tutorial to replace Nana's JavaScript/AWS Docker tutorial with a Python/Streamlit stack, local CI/CD, and a private local registry.

## User Review Required
> [!IMPORTANT]
> Please review this overall architecture and the steps below. Once you approve, we will execute this step-by-step, treating it as our next MLOps milestone.

## Open Questions
> [!WARNING]
> 1. **Production Server Emulation:** The simplest way to emulate a "production server" locally is to create a separate directory (e.g., `production_env/`) with a `docker-compose.prod.yml` that strictly pulls the compiled image from Harbor. Is this sufficient, or do you want to spin up a Docker-in-Docker (DinD) container that acts like a completely isolated virtual machine?
> 2. **Jenkins & Harbor Setup:** Running Jenkins and Harbor locally requires a fair amount of RAM (Harbor has several microservices). Are you comfortable running these as Docker containers on your local machine alongside your app?

## Proposed Architecture

This tutorial will replace the cloud components of Nana's tutorial with local equivalents to match an MLOps mindset:
- **Frontend/Backend:** JavaScript (Node.js) ➔ Python (Streamlit)
- **Database:** MongoDB & Mongo Express (Same)
- **Registry:** AWS ECR ➔ Harbor (Local Private Registry)
- **CI/CD & Server:** EC2 ➔ Jenkins & Local Simulated Production Server

## Step-by-Step Tutorial Plan

We will follow these steps sequentially, ensuring each one works before moving to the next.

### Step 1: The Local Development Environment
We will build the Streamlit application and connect it to MongoDB.
- Write `app.py` (Streamlit UI for User Profiles).
- Create a `Dockerfile` for the Streamlit app.
- Write `docker-compose.dev.yml` to spin up Streamlit, MongoDB, and Mongo Express.
- *Verification:* Access Streamlit and Mongo Express via localhost and add a user profile.

### Step 2: Set up Harbor (Private Registry)
We will set up Harbor to act as our local AWS ECR.
- Install Harbor locally using its official offline installer (which uses Docker Compose).
- Access the Harbor UI.
- Create a new private project/repository (e.g., `mlops-streamlit-app`).

### Step 3: Set up Jenkins (CI/CD)
We will run Jenkins locally to act as our CI/CD pipeline.
- Create a `docker-compose.jenkins.yml` to spin up Jenkins.
- We will mount the host's Docker socket (`/var/run/docker.sock`) into Jenkins so it can build and push Docker images.
- Set up Harbor credentials inside Jenkins.

### Step 4: The Jenkins Pipeline (`Jenkinsfile`)
We will create a pipeline script that defines the automation workflow.
- **Stage 1 (Build):** Jenkins builds the Streamlit Docker image.
- **Stage 2 (Test):** Run smoke/regression tests on the Python code (satisfying our SOLID/testing rules).
- **Stage 3 (Push):** Jenkins pushes the built image to Harbor.

### Step 5: Emulate Production Server & Deployment
We will simulate a production environment separate from our dev environment.
- Create a `production/` folder.
- Create `docker-compose.prod.yml` that relies entirely on the image hosted in Harbor (no local builds).
- **Stage 4 (Deploy):** The Jenkins pipeline will execute the docker-compose command in this production folder, simulating a remote deployment.

## Verification Plan
- **Automated Tests:** Python tests run in the Jenkins pipeline before pushing the image.
- **Manual Verification:** 
  - Ensure Harbor shows the pushed Docker image.
  - Verify the production Streamlit app runs on a different port than the dev app.
  - Confirm data persists correctly in the production MongoDB.
