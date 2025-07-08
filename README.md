# 🚀 AI Social Media Automation Suite

Welcome to the **AI Social Media Automation Suite** – your all-in-one solution for generating, enhancing, and posting content across all major social and blogging platforms, powered by AI and seamless API integrations.

---

## ✨ Why This Suite is One-of-a-Kind

- **100% Free & Open Source:** No subscriptions, no hidden fees, no paywalls. All features are available to everyone, forever.
- **Next-Level Image Generation:**
  - Instantly create stunning, platform-tailored images for every post using advanced AI (Pollinations, HuggingFace, OpenAI DALL·E, and more).
  - Images are generated on-the-fly to match your story, scenario, or mood—no stock photos, no boring visuals!
  - **No paid API keys required for image generation** (uses free endpoints and open models).
- **Automate Everything:**
  - One command posts to all your favorite platforms, with unique content and visuals for each.
  - Handles all platform quirks (flairs, tags, image uploads, text limits, etc.) automatically.
- **Perfect for Creators, Marketers, and Growth Hackers:**
  - Save hours every week and supercharge your online presence with AI-powered creativity.

---

## 🖼️ Unmatched AI Image Generation (for Free!)

- **Every post gets a unique, AI-generated image**—no manual searching, no copyright worries.
- **Multiple AI models** (Pollinations, HuggingFace, DALL·E, etc.) are used for maximum variety and quality.
- **Images are uploaded automatically** to Cloudinary or Imgur for seamless posting.
- **No cost, no premium keys needed**—all image generation is free and unlimited!

---

## 🌟 Features
- **One-click posting** to LinkedIn, Twitter/X, Reddit, Dev.to, Hashnode, Blogger, Disqus, Mastodon, Pinterest, Pixelfed, and more!
- **AI-powered content & image generation** (OpenAI, HuggingFace, Pollinations)
- **Automatic scenario selection** for creative, human-like posts
- **Image upload support** (Cloudinary, Imgur)
- **Handles platform-specific rules** (flairs, tags, truncation, etc.)
- **Easy credential management** via `.env` file

---

## 📋 Supported Platforms

| Platform    | API Docs Link                                              |
|------------|------------------------------------------------------------|
| Reddit     | https://www.reddit.com/dev/api/                            |
| Pixelfed   | https://pypi.org/project/pixelfed-python-api/              |
| Pinterest  | https://developers.pinterest.com/docs/api/v5/              |
| Blogger    | https://developers.google.com/blogger/docs/3.0/getting_started |
| Mastodon   | https://docs.joinmastodon.org/client/intro/                |
| Dev.to     | https://developers.forem.com/api/                          |
| Hashnode   | https://hashnode.com/api                                   |
| LinkedIn   | https://learn.microsoft.com/en-us/linkedin/                |
| Disqus     | https://disqus.com/api/docs/                               |
| Twitter/X  | https://developer.twitter.com/en/docs                      |

---

## 🛠️ Setup & Installation

1. **Clone this repository:**
   ```sh
   git clone <your-repo-url>
   cd <project-folder>
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Copy and configure environment variables:**
   ```sh
   cp .env.example .env
   # Then edit .env with your credentials
   ```

---

## 🔑 Generating API Credentials

Each platform requires its own API credentials. Here’s how to get them:

- **LinkedIn:**
  - Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
  - Create an app, set redirect URI, and copy `CLIENT_ID`, `CLIENT_SECRET`
- **Twitter/X:**
  - Apply for a developer account at [Twitter Developer Portal](https://developer.twitter.com/)
  - Create a project/app, generate API keys and tokens
- **Reddit:**
  - Visit [Reddit Apps](https://www.reddit.com/prefs/apps)
  - Create a script app, set redirect URI, copy `client_id`, `client_secret`
- **Dev.to:**
  - Go to [Dev.to Settings](https://dev.to/settings/account)
  - Generate an API key
- **Hashnode:**
  - Visit [Hashnode API](https://hashnode.com/api)
  - Generate a personal access token and publication ID
- **Blogger:**
  - Use [Google Cloud Console](https://console.developers.google.com/)
  - Enable Blogger API, create OAuth credentials
- **Disqus:**
  - Register an app at [Disqus API](https://disqus.com/api/applications/)
- **Mastodon:**
  - Register an app on your Mastodon instance ([docs](https://docs.joinmastodon.org/client/intro/))
- **Pinterest:**
  - Create an app at [Pinterest Developers](https://developers.pinterest.com/)
- **Pixelfed:**
  - Register an app on your Pixelfed instance ([docs](https://pixelfed.org/docs/))
- **Cloudinary/Imgur:**
  - [Cloudinary](https://cloudinary.com/) / [Imgur](https://api.imgur.com/oauth2/addclient)

> **Tip:** See `.env.example` for the full list of required variables for each platform.

---

## 🚦 Usage

- **Run all automations:**
  ```sh
  python run_automation.py
  ```
- **Customize or run a single platform:**
  Edit or call the relevant function in `run_automation.py` (e.g., `run_linkedin()`, `run_twitter()`, etc.)

---

## 💡 How It Works

1. **Content Generation:**
   - Uses OpenAI to generate creative, scenario-based posts for each platform
2. **Image Generation:**
   - Optionally generates images using Pollinations or HuggingFace
3. **API Posting:**
   - Authenticates and posts content (and images) to each platform using your credentials
4. **Handles Platform Rules:**
   - Adapts to each platform’s requirements (length, tags, flairs, etc.)

---

## 🧩 File Structure

- `run_automation.py` – Main entry point, runs all automations
- `core/` – All platform logic, authentication, content/image generation
- `.env.example` – Example environment variables (copy to `.env`)
- `requirements.txt` – Python dependencies

---

## 🛡️ Security
- **Never share your `.env` file or credentials.**
- Use environment variables for all secrets.

---

## 🤝 Contributing
Pull requests and issues are welcome! Please open an issue for bugs or feature requests.

---

## 📄 License
MIT License

---

> **Made with ❤️ for creators, marketers, and automation lovers!**
