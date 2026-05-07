# AudioDose — Deployment Guide
### How to Put Your App on the Internet Using Vercel or Netlify

---

## Understanding the Problem First

Before jumping into steps, it helps to understand **why** this setup is needed.

Your AudioDose app has **two parts** that do completely different jobs:

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (index.html)                               │
│  • The webpage the user sees                         │
│  • Buttons, camera, results cards                    │
│  • Just HTML, CSS, and JavaScript                    │
│  • Any hosting can run this — including Vercel       │
│    and Netlify                                       │
└─────────────────────────────────────────────────────┘
                        │
                        │ sends photo via HTTP
                        ↓
┌─────────────────────────────────────────────────────┐
│  BACKEND (app.py)                                    │
│  • The Python server running on YOUR laptop          │
│  • Loads the YOLOv8 model (best.pt ~22MB)            │
│  • Loads PyTorch (~1.5GB installed)                  │
│  • Does the actual pill detection                    │
│  • Returns results as JSON                           │
│  • CANNOT run on Vercel or Netlify                   │
└─────────────────────────────────────────────────────┘
```

**Why can't the backend run on Vercel or Netlify?**

Both platforms are designed for lightweight web apps, not machine learning.
Your app needs PyTorch and YOLOv8 which together are over 1.5GB installed —
Vercel has a 250MB limit and Netlify has a similar restriction. Even if the
files fit, the detection itself takes 1-3 seconds of heavy CPU/GPU work which
exceeds what these platforms allow for serverless functions.

---

## The Solution — Split the App

Since we can only use Vercel or Netlify for hosting, we use a tool called
**ngrok** to create a secure tunnel from the internet directly into your
laptop. Your laptop does the hard AI work, and Vercel/Netlify just serves
the webpage.

Here is how it looks when everything is running:

```
User's Phone/Browser
        │
        │  visits your Netlify/Vercel URL
        ↓
┌───────────────────┐
│  Netlify / Vercel │   ← free hosting, always on
│  (index.html)     │
└───────────────────┘
        │
        │  fetch("/detect") → goes to API_BASE URL
        ↓
┌───────────────────────────────────────┐
│  ngrok tunnel                         │
│  https://abc123.ngrok-free.app        │   ← public HTTPS URL
│  (running on ngrok's servers)         │
└───────────────────────────────────────┘
        │
        │  forwards traffic securely
        ↓
┌───────────────────────────────────────┐
│  YOUR LAPTOP (must be on and running) │
│  python start.py → uvicorn app:app    │
│  → loads best.pt → detects pills      │
└───────────────────────────────────────┘
```

The user never knows the detection is happening on your laptop. To them it
just looks like a normal website.

---

## What You Need

Before starting, make sure you have all of the following:

- Your trained `best.pt` model in the `AudioDose/models/` folder
- A GitHub account (free) — https://github.com
- A Netlify account (free) — https://netlify.com OR a Vercel account (free) — https://vercel.com
- An ngrok account (free) — https://ngrok.com
- Your `AudioDose` project folder with all files

---

## Part 1 — Set Up ngrok

ngrok is the tool that makes your laptop reachable from the internet.
Think of it as a phone number for your laptop — anyone can call it (send
requests to it) from anywhere in the world.

### Step 1.1 — Create a Free ngrok Account

Go to https://ngrok.com and click Sign Up. Use your email or sign in with
Google. The free tier is enough for this project.

### Step 1.2 — Get Your Auth Token

After signing in, go to:
```
https://dashboard.ngrok.com/get-started/your-authtoken
```

You will see a long string of random characters that looks like this:
```
2abc123XYZdef456_someMoreCharactersHere
```

Copy it — you will need it in the next step.

### Step 1.3 — Install ngrok Python Package

Open your Anaconda Prompt, activate your environment, and run:
```bash
conda activate yolov8_env
pip install pyngrok
```

### Step 1.4 — Paste Your Token into start.py

Open `AudioDose/start.py` in VS Code. Find this line near the top:
```python
NGROK_TOKEN = "PASTE_YOUR_NGROK_AUTH_TOKEN_HERE"
```

Replace `PASTE_YOUR_NGROK_AUTH_TOKEN_HERE` with your actual token:
```python
NGROK_TOKEN = "2abc123XYZdef456_someMoreCharactersHere"
```

Save the file.

---

## Part 2 — Deploy Frontend to Netlify

Netlify is the simplest option — you can deploy by just dragging a folder.

### Step 2.1 — Create a Netlify Account

Go to https://netlify.com and sign up for free. You can use GitHub to sign in.

### Step 2.2 — Deploy by Drag and Drop

This is the easiest method and requires no command line tools.

1. Log in to Netlify
2. From the main dashboard, look for the section that says **"Want to deploy a new site without connecting to Git?"**
3. You will see a drag and drop area that says **"Drag and drop your site output folder here"**
4. Open File Explorer and navigate to your `AudioDose` folder
5. Drag the **`templates`** folder (the one containing `index.html`) and drop it into that Netlify area
6. Wait 10-30 seconds for it to upload and process
7. Netlify will give you a random URL like `https://amazing-otter-12345.netlify.app`

That is your public frontend URL. Write it down.

### Step 2.3 — (Optional) Rename Your Site

The random URL like `amazing-otter-12345` is hard to remember. To change it:

1. Go to your site in Netlify dashboard
2. Click **Site settings → General → Site details → Change site name**
3. Type something like `audiodose-ph` → Save
4. Your URL becomes `https://audiodose-ph.netlify.app`

---

## Part 3 — Deploy Frontend to Vercel (Alternative to Netlify)

Use this if you prefer Vercel over Netlify. You only need to do one of
Part 2 or Part 3 — not both.

### Step 3.1 — Push Your Project to GitHub

Vercel works by connecting to a GitHub repository. Open Anaconda Prompt
in your `AudioDose` folder and run:

```bash
git init
git add templates/ vercel.json
git commit -m "AudioDose frontend"
git branch -M main
```

Then go to https://github.com/new, create a new repository called
`audiodose`, then run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/audiodose.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3.2 — Connect to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click **Add New Project**
3. Find your `audiodose` repository and click **Import**
4. Vercel will auto-detect the `vercel.json` file
5. Click **Deploy**
6. After 1-2 minutes you get a URL like `https://audiodose.vercel.app`

---

## Part 4 — Start Your Backend (Every Session)

Every time you want the app to be available online, you need to run this
on your laptop. The moment you close your laptop or stop the script, the
app will stop working for users.

### Step 4.1 — Run the Launcher

Open Anaconda Prompt, navigate to your project, and run:

```bash
conda activate yolov8_env
cd C:\Users\JanMaviric Alcantara\Downloads\AudioDose
python start.py
```

After about 5 seconds you will see something like this:

```
=======================================================
  AudioDose — Public Server Launcher
=======================================================

[→] Starting FastAPI server...
[→] Opening ngrok tunnel...

=======================================================
  ✓ Public URL: https://abc123.ngrok-free.app
  ✓ Local URL : http://localhost:8000
=======================================================

  → Copy this URL into your Vercel/Netlify frontend:

     https://abc123.ngrok-free.app

  → Keep this terminal open while the app is running.
  → Press Ctrl+C to stop.
```

**Copy the Public URL.** You need it in the next step.

### Step 4.2 — Update the Frontend with the ngrok URL

This is the step most people forget. Every time you run `start.py`, ngrok
gives you a **new different URL**. You must update the frontend with this
new URL each time, otherwise the webpage will not know where to send
detection requests.

Open `AudioDose/templates/index.html` in VS Code. Press `Ctrl+F` and
search for `API_BASE`. You will find this line near the top of the
`<script>` section:

```javascript
const API_BASE = "";
```

Replace it with your ngrok URL in quotes:

```javascript
const API_BASE = "https://abc123.ngrok-free.app";
```

Save the file.

### Step 4.3 — Redeploy the Frontend

Since you changed `index.html`, you need to push the update to your
hosting so users get the new version.

**For Netlify (drag and drop):**
Go back to https://app.netlify.com, open your site, go to **Deploys**,
and drag the `templates` folder into the deploy drop zone again.

**For Vercel (GitHub):**
```bash
git add templates/index.html
git commit -m "Update API_BASE with new ngrok URL"
git push
```
Vercel automatically redeploys whenever you push to GitHub.

---

## Part 5 — Test the Full Setup

With everything running, here is how to verify it works end to end:

1. Make sure `start.py` is running in Anaconda Prompt and you can see the ngrok URL
2. Open your Netlify or Vercel URL in a browser on your phone or another device
3. Go to the Scan tab
4. Open the camera or upload a photo
5. Tap Scan
6. You should see detections come back within a few seconds

If the scan fails with an error, check the Troubleshooting section below.

---

## The Big Catch — ngrok Free Tier URL Changes

This is the main limitation of the free setup. Every time you run
`start.py`, ngrok gives you a completely different URL. This means:

- Session 1: `https://abc123.ngrok-free.app`
- Session 2: `https://xyz789.ngrok-free.app`
- Session 3: `https://def456.ngrok-free.app`

Each time you get a new URL, you have to update `API_BASE` in `index.html`
and redeploy to Netlify or Vercel. This is annoying but it is free.

**The paid fix:** ngrok's paid plan ($10/month) lets you claim a permanent
static URL like `https://audiodose.ngrok.app` that never changes. Once
you set this up, you never need to update `API_BASE` again.

---

## Troubleshooting

### "No pills detected" but the camera is working

The frontend is loaded but the API call is failing. Check:

1. Is `start.py` running in Anaconda Prompt? It must stay open.
2. Is `API_BASE` in `index.html` set to your current ngrok URL?
3. Did you redeploy after changing `API_BASE`?
4. Open your browser's DevTools (F12) → Network tab → look for a failed
   `/detect` request and check the error message.

### "Failed to fetch" error in the browser console

This means the browser is blocking the request. Two possible causes:

- The ngrok URL in `API_BASE` is wrong or outdated — update it and redeploy
- Your laptop is asleep or the `start.py` script stopped — restart it

### Camera doesn't work on the deployed site

Mobile browsers only allow camera access on HTTPS pages. Netlify and Vercel
both serve over HTTPS automatically, and ngrok also gives you HTTPS, so
this should work. If it still fails, make sure you are opening the Netlify
or Vercel URL and not the `file://` local file.

### ngrok shows "ERR_NGROK_6022" or similar

Your free ngrok session has expired (free accounts get 2 hours per session).
Just stop `start.py` with Ctrl+C, run it again, and update `API_BASE` with
the new URL.

### "Model not found" error from the backend

The `best.pt` file is missing. Make sure it exists at
`AudioDose/models/best.pt`. If it does not exist, you need to run training
first: `python train.py --model yolov8s.pt`

---

## Quick Reference — Every Time You Start

```
1. Open Anaconda Prompt
   conda activate yolov8_env
   cd C:\Users\JanMaviric Alcantara\Downloads\AudioDose
   python start.py

2. Copy the ngrok URL from the terminal output

3. Open AudioDose/templates/index.html in VS Code
   Find:    const API_BASE = "...old url...";
   Replace: const API_BASE = "https://YOUR-NEW-URL.ngrok-free.app";
   Save the file.

4. Redeploy frontend:
   Netlify → drag templates/ folder to deploy area
   Vercel  → git add . && git commit -m "update url" && git push

5. Open your Netlify/Vercel URL — app is live!
```

---

## Summary of All Files and What They Do

| File | Purpose |
|---|---|
| `templates/index.html` | The frontend — deployed to Netlify or Vercel |
| `app.py` | The FastAPI backend — runs on your laptop |
| `start.py` | Starts `app.py` + opens ngrok tunnel together |
| `netlify.toml` | Tells Netlify where to find `index.html` |
| `vercel.json` | Tells Vercel how to serve the static frontend |
| `models/best.pt` | Your trained YOLOv8 pill detection model |
| `utils/pill_database.json` | Pill info database loaded by `app.py` |

---

*AudioDose — Built for Philippine healthcare.*
*Always consult a licensed pharmacist or physician before taking any medication.*
