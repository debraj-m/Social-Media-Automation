# Social Media Automation

This project provides automation for posting content to major social and professional platforms using their APIs. It leverages OpenAI for content generation and supports OAuth-based authentication for each platform where required.

## Supported Platforms
- LinkedIn
- Twitter
- Pinterest
- Reddit
- Mastodon
- Medium
- Dev.to
- Hashnode
- Ghost
- WordPress

## .env Setup
Refer to `.env.example` for the required environment variables. Copy `.env.example` to `.env` and fill in your credentials. Example keys:

```
# LinkedIn
LINKEDIN_CLIENT_ID=""
LINKEDIN_CLIENT_SECRET=""
LINKEDIN_REDIRECT_URI=""
LINKEDIN_SCOPE=""

# Twitter
TWITTER_USERNAME=""
TWITTER_EMAIL=""
TWITTER_PASSWORD=""

# Pinterest
PINTEREST_CLIENT_ID=""
PINTEREST_CLIENT_SECRET=""
PINTEREST_ACCESS_TOKEN=""

# Reddit
REDDIT_CLIENT_ID=""
REDDIT_CLIENT_SECRET=""
REDDIT_USER_AGENT=""
REDDIT_USERNAME=""
REDDIT_PASSWORD=""

# Mastodon
MASTODON_CLIENT_ID=""
MASTODON_CLIENT_SECRET=""
MASTODON_ACCESS_TOKEN=""
MASTODON_INSTANCE_URL=""

# Medium
MEDIUM_INTEGRATION_TOKEN=""

# Dev.to
DEVTO_API_KEY=""

# Hashnode
HASHNODE_API_KEY=""

# Ghost
GHOST_ADMIN_API_KEY=""
GHOST_API_URL=""

# WordPress
WORDPRESS_CLIENT_ID=""
WORDPRESS_CLIENT_SECRET=""
WORDPRESS_USERNAME=""
WORDPRESS_PASSWORD=""
WORDPRESS_SITE_URL=""

# OpenAI
OPENAI_API_KEY=""
```

## Running Steps
1. Install dependencies from `requirements.txt` using pip:
   ```sh
   pip install -r requirements.txt
   ```
2. Set up your `.env` file as described above.
3. Execute the file `run_automation.py` to start the automation and follow the prompts to select the platform and post content.

## Project Structure
- `core/automation/` - Contains platform-specific automation logic (e.g., LinkedIn, Twitter, Pinterest, etc.).
- `core/content_generation/` - Contains content generation logic using OpenAI.
- `core/auth/<platform>/` - Contains OAuth or API key logic for each platform.
- `env/` - Stores tokens and environment-specific files.

## Notes
- Each platform's credentials and tokens are managed via environment variables and stored securely in the `env/` directory.
- Posting logic and authentication for each platform is modular and follows a consistent structure for easy extension.
- See the code and comments for details on how to add new platforms or customize posting logic.
