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
