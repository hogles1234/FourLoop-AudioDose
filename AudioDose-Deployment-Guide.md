# AudioDose — GitHub Codespaces Deployment Guide
### Run Your Full App on the Cloud Using GitHub — No Laptop Required

---

## Table of Contents

1. [What is GitHub Codespaces?](#1-what-is-github-codespaces)
2. [How It Works](#2-how-it-works)
3. [What You Need Before Starting](#3-what-you-need-before-starting)
4. [Step 1 — Prepare Your Project](#step-1--prepare-your-project)
5. [Step 2 — Push to GitHub](#step-2--push-to-github)
6. [Step 3 — Upload Your Model](#step-3--upload-your-model)
7. [Step 4 — Add Codespaces Config](#step-4--add-codespaces-config)
8. [Step 5 — Open GitHub Codespaces](#step-5--open-github-codespaces)
9. [Step 6 — Run the App](#step-6--run-the-app)
10. [Step 7 — Make it Public](#step-7--make-it-public)
11. [Every Time You Want the App Online](#every-time-you-want-the-app-online)
12. [Free Tier Limits](#free-tier-limits)
13. [Troubleshooting](#troubleshooting)
14. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## 1. What is GitHub Codespaces?

GitHub Codespaces is a full cloud computer that runs inside your browser,
provided by GitHub for free. When you open a Codespace on your project,
GitHub spins up a Linux machine in the cloud, installs all your Python
packages, and runs your code — all without touching your laptop.

The important thing for AudioDose is that Codespaces can run **real Python
servers** including FastAPI, PyTorch, and YOLOv8. This is something Vercel
and Netlify cannot do because they are limited to lightweight serverless
functions. Codespaces gives you a full machine.

---

## 2. How It Works

When everything is set up, this is what happens:

```
User's Phone or Browser
        │
        │  visits your Codespaces public URL
        │  e.g. https://username-audiodose-abc123.app.github.dev
        ↓
┌─────────────────────────────────────────────┐
│  GitHub Codespaces (cloud computer)          │
│                                             │
│  ┌─────────────────┐  ┌──────────────────┐  │
│  │  index.html     │  │  app.py          │  │
│  │  (frontend)     │  │  (FastAPI)       │  │
│  │                 │  │                  │  │
│  │  Camera / UI    │  │  YOLOv8 model    │  │
│  │  Scan buttons   │  │  best.pt         │  │
│  │  Results cards  │  │  Detection logic │  │
│  └─────────────────┘  └──────────────────┘  │
│                                             │
│  Both frontend AND backend run here         │
│  No ngrok needed. No laptop needed.         │
└─────────────────────────────────────────────┘
```

Both the frontend and backend live in the same Codespace. The URL that
GitHub gives you is public and uses HTTPS automatically, which means the
camera feature works on mobile without any extra setup.

---

## 3. What You Need Before Starting

- A GitHub account — https://github.com (free)
- Your trained `best.pt` model in `AudioDose/models/`
- Your complete `AudioDose` project folder
- A browser (Chrome or Edge recommended)
- That is all — no other accounts or tools needed

---

## Step 1 — Prepare Your Project

Before pushing to GitHub, you need to create two files that tell Git which
files to ignore and tell GitHub how to set up the Codespace.

### 1.1 — Create a `.gitignore` File

This file tells Git NOT to upload certain things. The YOLOv8 model and
dataset are too large and the virtual environment does not need to go to
GitHub since it will be reinstalled automatically.

Create a file called `.gitignore` in the root of your `AudioDose` folder.
Open Notepad or VS Code, paste the following, and save it as `.gitignore`
(make sure there is a dot at the start and no `.txt` extension):

```
# Python virtual environments
venv/
yolov8_env/
__pycache__/
*.pyc
*.pyo

# Model weights (uploaded separately via GitHub LFS)
*.pt
*.onnx
*.engine

# Dataset (too large — stays on your machine)
dataset/
runs/
yolov8s.pt

# Uploaded images from the app
static/uploads/

# System files
.DS_Store
Thumbs.db
desktop.ini

# Environment variables
.env
```

### 1.2 — Create the Codespaces Configuration Folder

Create a folder called `.devcontainer` inside your `AudioDose` folder.
Inside that folder, create a file called `devcontainer.json` with this
content:

```json
{
  "name": "AudioDose",
  "image": "mcr.microsoft.com/devcontainers/python:3.10",
  "postCreateCommand": "pip install -r requirements.txt",
  "forwardPorts": [8000],
  "portsAttributes": {
    "8000": {
      "label": "AudioDose App",
      "onAutoForward": "openBrowser",
      "visibility": "public"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
    }
  }
}
```

What each part does:

| Setting | What it does |
|---|---|
| `image` | Uses Python 3.10 Linux environment |
| `postCreateCommand` | Automatically runs `pip install -r requirements.txt` when the Codespace starts |
| `forwardPorts` | Exposes port 8000 so the app is accessible |
| `visibility: public` | Makes the URL accessible to anyone without logging in |
| `onAutoForward: openBrowser` | Automatically opens the app in a new tab when it starts |

Your project folder should now look like this:

```
AudioDose/
├── .devcontainer/
│   └── devcontainer.json     ← NEW
├── .gitignore                ← NEW
├── app.py
├── train.py
├── start.py
├── requirements.txt
├── templates/
│   └── index.html
├── utils/
│   └── pill_database.json
└── models/
    └── best.pt               ← uploaded separately
```

---

## Step 2 — Push to GitHub

### 2.1 — Create a New Repository on GitHub

1. Go to https://github.com and log in
2. Click the `+` icon in the top right → **New repository**
3. Name it `audiodose`
4. Set it to **Public** (required for free Codespaces on the free tier)
5. Do NOT check "Add a README" — leave everything unchecked
6. Click **Create repository**

### 2.2 — Push Your Project

Open Anaconda Prompt, navigate to your project folder, and run these
commands one by one:

```bash
cd C:\Users\JanMaviric Alcantara\Downloads\AudioDose

git init
git add .
git commit -m "AudioDose initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/audiodose.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

When prompted, enter your GitHub username and password. If GitHub asks for
a personal access token instead of a password, generate one at:
```
https://github.com/settings/tokens
```
Click **Generate new token (classic)**, check the `repo` scope, generate,
and use that as your password.

### 2.3 — Verify the Push

Go to `https://github.com/YOUR_USERNAME/audiodose` in your browser. You
should see all your project files listed there. The `models/` folder will
be empty or missing — that is expected, we handle the model next.

---

## Step 3 — Upload Your Model

The `best.pt` file is around 22MB which is fine for GitHub but it was
excluded by `.gitignore` so we need to upload it separately. There are
two ways to do this.

### Option A — Upload Through the GitHub Website (Easiest)

1. Go to your repository on GitHub
2. Click **Add file → Create new file**
3. Type `models/placeholder.txt` in the name field and click commit — this creates the `models/` folder
4. Go back to the repository, click into the `models/` folder
5. Click **Add file → Upload files**
6. Drag and drop your `best.pt` file from `AudioDose/models/`
7. Click **Commit changes**

### Option B — Use Git Large File Storage (For Developers)

GitHub LFS is designed for large files like model weights. Run these
commands in Anaconda Prompt:

```bash
# Install Git LFS
git lfs install

# Tell LFS to track .pt files
git lfs track "*.pt"

# Add the tracking config
git add .gitattributes

# Add and push the model
git add models/best.pt
git commit -m "Add YOLOv8 model via LFS"
git push
```

You may need to install Git LFS separately from https://git-lfs.com first.

---

## Step 4 — Add Codespaces Config

If you already created the `.devcontainer` folder in Step 1 and pushed it,
you can skip this step. If not, push it now:

```bash
git add .devcontainer/
git add .gitignore
git commit -m "Add Codespaces config"
git push
```

---

## Step 5 — Open GitHub Codespaces

1. Go to your repository page on GitHub:
   ```
   https://github.com/YOUR_USERNAME/audiodose
   ```

2. Click the green **`<> Code`** button (top right of the file list)

3. Click the **Codespaces** tab

4. Click **Create codespace on main**

GitHub will now:
- Create a new Linux virtual machine in Microsoft Azure
- Clone your repository onto it
- Install Python 3.10
- Run `pip install -r requirements.txt` automatically
- Open a VS Code editor in your browser

This takes about **3 to 5 minutes** the first time. You will see a loading
screen with setup logs. Wait until it finishes fully before continuing.

> The free GitHub account gives you 2 CPU cores and 8GB RAM which is enough
> to run AudioDose. The model loads and runs on CPU in the Codespace.

---

## Step 6 — Run the App

Once the Codespace is ready, you will see a VS Code editor in your browser
with a terminal at the bottom. If the terminal is not visible, press
`` Ctrl+` `` to open it.

In the terminal, run:

```bash
python app.py
```

You will see the FastAPI startup output:

```
==================================================
  AudioDose — FastAPI Server
  http://localhost:8000
==================================================
INFO:     Started server process
INFO:     Waiting for application startup.
[→] Loading model from models/best.pt…
[✓] Model loaded.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

A popup will appear at the bottom right of the screen saying something like:
**"Your application running on port 8000 is available. Open in Browser."**

Click **Open in Browser**. Your AudioDose app will open in a new tab.

---

## Step 7 — Make it Public

By default, the Codespace URL is private — only you can see it when logged
in to GitHub. To share it with others:

### Method 1 — VS Code Ports Tab

1. Look at the bottom panel in VS Code (Codespaces)
2. Click the **Ports** tab (next to Terminal)
3. Find port `8000` in the list
4. Right-click on it
5. Click **Port Visibility → Public**

The lock icon next to the port will disappear, confirming it is now public.

### Method 2 — Automatic via devcontainer.json

If you used the `devcontainer.json` from Step 1.2 with
`"visibility": "public"`, this is done automatically when the Codespace
starts. No manual steps needed.

### Get the Public URL

After making it public, hover over port 8000 in the Ports tab and click
the **copy icon** next to the URL. It will look like:

```
https://username-audiodose-abc123defg.app.github.dev
```

Share this URL with anyone. They can open it in their browser and use the
full app including camera scanning. The URL stays the same for the lifetime
of this Codespace — it only changes if you delete and recreate the Codespace.

---

## Every Time You Want the App Online

After the first setup, here is your workflow each session:

```
1. Go to github.com/YOUR_USERNAME/audiodose

2. Click the green <> Code button → Codespaces tab

3. Click on your existing Codespace to resume it
   (do NOT create a new one every time — use the same one)

4. Wait for it to load (~30 seconds to resume vs 3-5 min to create)

5. In the terminal, run:
   python app.py

6. Click "Open in Browser" when the popup appears

7. Share the URL from the Ports tab — app is live!
```

> Always resume your existing Codespace rather than creating a new one.
> Creating a new one each time wastes your free hours and gives you a
> different URL. Resuming the same one is faster and keeps the same URL.

---

## Free Tier Limits

GitHub gives free accounts the following Codespaces allowance each month:

| Resource | Free Allowance |
|---|---|
| Compute hours (2-core) | 120 hours per month |
| Storage | 15 GB per month |
| Machines | Up to 2 active Codespaces |

120 hours per month is 4 hours per day every day. This is enough for
regular development and demos. The counter resets on the 1st of each month.

### Auto-Sleep

Codespaces automatically stops after **30 minutes of inactivity** to save
your free hours. When it stops, the URL goes offline and users will see an
error. To bring it back:

1. Go to https://github.com/codespaces
2. Find your stopped Codespace
3. Click the `...` menu → **Resume**
4. Run `python app.py` again in the terminal

### Check Your Usage

To see how many hours you have left this month:
```
https://github.com/settings/billing
```
Scroll down to the Codespaces section.

---

## Troubleshooting

### App opens but shows a blank page or error

The server might still be starting. Wait 10 seconds and refresh the page.
If it still fails, check the terminal in Codespaces for error messages.

### "Model not found at models/best.pt"

The model file was not uploaded. Go to your GitHub repository, check if
`models/best.pt` exists. If not, go back to Step 3 and upload it.

### "ModuleNotFoundError: No module named 'ultralytics'"

The packages did not install correctly. Run this in the Codespace terminal:
```bash
pip install -r requirements.txt
```

### Camera does not work in the browser

Make sure the URL starts with `https://`. GitHub Codespaces always provides
HTTPS so this should work. If the browser blocks it, click the lock icon
in the address bar and allow camera access for this site.

### Port 8000 is not showing in the Ports tab

Run `python app.py` first. The port only appears in the Ports tab after
something is actually running on it.

### Codespace takes too long to create

This is normal for the first time since it installs PyTorch and ultralytics
which are large packages. Subsequent resumes are much faster (30 seconds)
because the packages are already installed and cached.

### "This Codespace is stopped" when visiting the URL

The Codespace auto-slept due to inactivity. Go to
https://github.com/codespaces, resume it, and run `python app.py` again.

### Free hours ran out

You will get an email from GitHub warning you when hours are low. If they
run out, the Codespace cannot run until the next month. To avoid this, stop
the Codespace manually when you are done:

Go to https://github.com/codespaces → click `...` → **Stop codespace**.
This stops the timer. Only resume it when you need the app to be live.

---

## Updating Your Code

When you make changes to your project files locally (on your laptop) and
want them to appear in the Codespace, push them to GitHub:

```bash
# On your laptop — after making changes
git add .
git commit -m "describe what you changed"
git push
```

Then in the Codespace terminal, pull the latest changes:
```bash
git pull
python app.py
```

---

## Quick Reference Cheat Sheet

### First-Time Setup (do once)
```
1. Create .gitignore and .devcontainer/devcontainer.json
2. git init → git add . → git commit → git push
3. Upload models/best.pt to GitHub manually
4. Open Codespaces from the green Code button → Create codespace on main
5. Wait for setup → run: python app.py
6. Ports tab → right-click port 8000 → Public
7. Copy and share the URL
```

### Every Session After That
```
1. Go to github.com/YOUR_USERNAME/audiodose
2. Green Code button → Codespaces → click existing Codespace (resume)
3. Terminal: python app.py
4. Open in Browser → share the URL from Ports tab
5. When done: go to github.com/codespaces → Stop codespace
```

### Push Code Changes
```
On laptop:  git add . → git commit -m "message" → git push
In Codespace terminal: git pull → python app.py
```

### Check Free Hours Remaining
```
https://github.com/settings/billing → scroll to Codespaces
```

---

## Comparison With Other Options

| Method | Backend Support | Always Online | Free | Difficulty |
|---|---|---|---|---|
| GitHub Codespaces | ✅ Full Python/PyTorch | ❌ Only when open | ✅ 120hrs/mo | Easy |
| Vercel + ngrok | ✅ Via tunnel | ❌ Laptop must be on | ✅ Yes | Medium |
| Render.com | ✅ Full Python | ✅ Yes | ⚠️ Sleeps free tier | Medium |
| Hugging Face Spaces | ✅ Full ML support | ✅ Yes | ✅ Yes | Medium |
| Local only | ✅ Full | ❌ Same network only | ✅ Yes | Easy |

For a student project or demo, **GitHub Codespaces is the best option**
because it is free, requires no extra accounts, the URL is always HTTPS
(camera works on mobile), and everything lives in one place on GitHub.

---

*AudioDose — Built for Philippine healthcare.*
*Always consult a licensed pharmacist or physician before taking any medication.*
