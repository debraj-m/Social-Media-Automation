# Social Media Automation

This project provides automation for posting content to social media platforms such as LinkedIn (and Twitter ) using their APIs. It leverages OpenAI for content generation and supports OAuth-based authentication(LinkedIn).

# .env setup
Refer to `.env.example` for the required environment variables. Copy `.env.example` to `.env` and fill in your credentials:

```
CLIENT_ID=""
CLIENT_SECRET=""
REDIRECT_URI=""
SCOPE=""
TOKEN_PATH="env/linkedin_token.json" // Path to store generated linked token from oAuth
OPENAI_API_KEY=""
TWITTER_USERNAME=""
TWITTER_EMAIL=""
TWITTER_PASSWORD=""
QUORA_EMAIL=""
QUORA_PASSWORD=""
MEDIUM_EMAIL=""
MEDIUM_PASSWORD=""
```

## Running Steps
1. Install dependencies from `requirements.txt` using pip.
2. Set up your `.env` file as described above.
3. Execute the file `run_automation.py` to start the automation and follow the prompts to select the platform and post content.

## Project Structure
- `core/automation/` - Contains platform-specific automation logic (e.g., LinkedIn, Twitter).
- `core/content_generation/` - Contains content generation logic using OpenAI.
- `core/auth/linkedin/` - Contains LinkedIn OAuth logic.
- `env/` - Stores tokens and environment-specific files.
