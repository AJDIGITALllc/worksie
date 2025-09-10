# 🛠 Worksie App

Worksie is a full-stack field operations platform built to outpace tools like CompanyCam by integrating advanced project documentation, CRM, scheduling, payment processing, and AI-powered reports into one system.

## 🚀 Features
- GPS-tagged photo & video capture
- 3D LiDAR scan + floorplan generation
- AI-generated job reports (PDF)
- CRM pipeline with task management
- Real-time chat, notifications, and permissions
- Stripe-integrated payments + invoices
- Template marketplace for checklists & forms

## 📁 Folder Structure
Organized by the Soulful Coder 6-Pillar System:

```
src/
├── components/
├── pages/
├── logic/
├── hooks/
├── context/
public/
assets/
prompts/
dataset/
docs/
scripts/
```

## 📦 Tech Stack
- React + TailwindCSS
- Firebase Hosting + Firestore
- Stripe API, Claude + GPT agents
- Replit for frontend & compute

## 🧠 Claude Agent Prompts
Stored in `/prompts`:
- blueprint_mapper_agent
- deployment_trigger_agent
- vibe_designer_agent
- training_orchestrator_agent

## ⚙️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/worksie.git
cd worksie
npm install
npm run dev
```

## 🔁 Deploy to Firebase
```bash
npm run build
firebase deploy
```

## 🤖 Train with Claude
Upload `worksie_training_schema.jsonl` and prompts into Claude Code and run:
```txt
"Use this schema and these agents to scaffold Worksie as a full-stack Firebase + React app."
```

## 🔥 Firebase Configuration

This project uses Firebase for push notifications. To connect to your Firebase project, you will need to set up your environment variables.

1.  **Create a `.env` file:** In the root of the `Worksie` directory, create a new file named `.env`.

2.  **Add your Firebase credentials:** Copy the contents of `.env.example` into your new `.env` file and replace the placeholder values with your actual Firebase project credentials.

    ```
    VITE_FIREBASE_API_KEY="YOUR_API_KEY"
    VITE_FIREBASE_AUTH_DOMAIN="YOUR_AUTH_DOMAIN"
    VITE_FIREBASE_PROJECT_ID="YOUR_PROJECT_ID"
    VITE_FIREBASE_STORAGE_BUCKET="YOUR_STORAGE_BUCKET"
    VITE_FIREBASE_MESSAGING_SENDER_ID="YOUR_MESSAGING_SENDER_ID"
    VITE_FIREBASE_APP_ID="YOUR_APP_ID"
    ```

3.  **Configure the Service Worker:** The Firebase service worker (`public/firebase-messaging-sw.js`) cannot access environment variables directly. You must manually open this file and replace the placeholder Firebase credentials with your actual project credentials.

Once you have completed these steps, the application will be able to connect to your Firebase project and receive push notifications.

## 📡 Firebase Remote Config

This project uses Firebase Remote Config to allow for dynamic configuration of the application. The configuration is stored in the `config/worksie-remote-config.json` file.

### Importing the Configuration

You can import this configuration into your Firebase project using the Firebase CLI or the REST API.

**Using the REST API (example):**

1.  **Get an access token:**
    ```bash
    ACCESS_TOKEN=$(gcloud auth print-access-token)
    ```

2.  **Push the configuration:**
    ```bash
    curl -X PUT \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json; UTF-8" \
     -d @config/worksie-remote-config.json \
     "https://firebaseremoteconfig.googleapis.com/v1/projects/YOUR_PROJECT_ID/remoteConfig"
    ```
    (Replace `YOUR_PROJECT_ID` with your actual Firebase project ID.)

### Using the Configuration in the App

The application is already set up to fetch and use the Remote Config values. The main logic is in `src/logic/remoteConfig.js`.

The `PromoBanner` component and the primary color are currently controlled by Remote Config. You can extend this to other parts of the application as needed.
