# FUCK-UDEMY – UaaS | Udemy as a Service

Automate video playing on platforms like Udemy with stealth, precision, and style.  
Bypasses annoying restrictions using stealth-chromedriver, plays multiple videos in parallel, simulates human behavior, and shuts down cleanly.

![Preview](f-udemy.jpg)
---

## 🚀 Features

- 🎭 Uses `undetected_chromedriver` to avoid Cloudflare detection  
- 🕵️ Simulates human interaction
- 🐳 Ready for Dockerized deployment   
- 🔀 Handles multiple video tabs in parallel   

---

> ⚠️ **Warning:** Be sure to *manually* disable the "Autoplay" setting in the video player's gear menu. Yes, Udemy likes to help you binge-learn endlessly, but for our script to track views properly and close tabs at the end of a video, we *really* need that autoplay off.

## 📦 Installation

```bash
git clone https://github.com/Bruckyy/fuck-udemy.git
cd fuck-udemy
python -m venv .env
source .env/bin/activate  # or .env\Scripts\activate on Windows
pip install -r requirements.txt
```

## 🔐 Setup cookies

Create a file called .cookies or just copy the template .cookies.tpl at the root with your session tokens:

```
ACCESS_TOKEN=your_access_token_here
DJ_SESSION_ID=your_dj_session_id_here
```
You can grab these from your browser’s DevTools after logging into Udemy.

## 📹 Prepare your video list

Create a file called videos.txt and list the URLs of the videos you want to play:
```
https://www.udemy.com/course/.../
https://www.udemy.com/course/.../
```

## 🧪 Usage

```bash
python fuck-udemy.py <options>
```

## 🐳 Docker

Docker need absolute paths for videos.txt and .cookies files on your local system otherwise it will not work
```
docker build -t fuck-udemy .
docker run -it --rm -v "$PWD/videos.txt:/app/videos.txt" -v "$PWD/.cookies:/app/.cookies" fuck-udemy <options>
```

## 🧠 Tips

- Use --no-headless if you’re debugging or want to verify things visually.
- Don’t forget to keep your cookies fresh if Udemy logs you out.
- By default, the script runs for 2 hours. You can modify this duration using the `--max-runtime` option, where the time is specified in hours. For example, to run the script for 5 hours, use `--max-runtime 5`.
- Use `--max-tabs` to set the maximum tabs per driver (can help to improve stability).

## 💻 Resource Consumption
Since the script runs multiple instances of Google Chrome, it’s important to be aware of its resource consumption. Each video opened in a new tab consumes more memory and CPU resources. The more videos you add to the videos.txt file, the more resources the script will use.

Just so you know, 40 videos will happily consume around 6GB of RAM. Yes, you read that right.

So go ahead, add 100 videos to the list and watch your machine melt. Fun times.

