# Social Media Automation

A comprehensive Python-based automation tool for posting content to multiple social media platforms including LinkedIn, Twitter, Quora, and Medium. This project leverages OpenAI for intelligent content generation and supports OAuth-based authentication for secure platform integration.

## Features

- **Multi-Platform Support**: Automate posting to LinkedIn, Twitter, Quora, and Medium
- **AI-Powered Content Generation**: Uses OpenAI API for intelligent content creation
- **OAuth Authentication**: Secure authentication for LinkedIn using OAuth 2.0
- **Credential Management**: Support for various authentication methods across platforms
- **Modular Architecture**: Clean separation of concerns with dedicated modules for each platform

## Supported Platforms

- **LinkedIn** - OAuth 2.0 authentication
- **Twitter** - Username/email and password authentication
- **Quora** - Email and password authentication
- **Medium** - Email and password authentication

## Project Structure

```
Social-Media-Automation/
├── core/
│   ├── automation/          # Platform-specific automation logic
│   ├── content_generation/  # OpenAI-powered content generation
│   └── auth/
│       └── linkedin/        # LinkedIn OAuth implementation
├── env/                     # Token storage and environment files
├── run_automation.py        # Main execution script
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/debraj-m/Social-Media-Automation.git
   cd Social-Media-Automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

## Configuration

Edit the `.env` file with your credentials and API keys:

```bash
# LinkedIn OAuth Configuration
CLIENT_ID=""                    # LinkedIn App Client ID
CLIENT_SECRET=""               # LinkedIn App Client Secret
REDIRECT_URI=""               # OAuth redirect URI
SCOPE=""                      # LinkedIn API scopes
TOKEN_PATH="env/linkedin_token.json"  # Path to store LinkedIn OAuth token

# OpenAI Configuration
OPENAI_API_KEY=""             # Your OpenAI API key

# Twitter Credentials
TWITTER_USERNAME=""           # Twitter username
TWITTER_EMAIL=""              # Twitter email
TWITTER_PASSWORD=""           # Twitter password

# Quora Credentials
QUORA_EMAIL=""                # Quora email
QUORA_PASSWORD=""             # Quora password

# Medium Credentials
MEDIUM_EMAIL=""               # Medium email
MEDIUM_PASSWORD=""            # Medium password
```

## Usage

1. **Run the automation script**
   ```bash
   python run_automation.py
   ```

2. **Follow the interactive prompts** to:
   - Select the social media platform
   - Choose content generation options
   - Configure posting parameters

3. **First-time LinkedIn setup**: The application will guide you through the OAuth flow to authenticate with LinkedIn.

## API Setup Instructions

### LinkedIn API
1. Create a LinkedIn Developer account at [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create a new app and configure OAuth 2.0 settings
3. Add the required scopes for posting content
4. Set up the redirect URI in your app settings

### OpenAI API
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key from your dashboard
3. Add the key to your `.env` file

### Twitter API (if using API instead of credentials)
1. Apply for Twitter Developer account
2. Create a new app in the Twitter Developer Portal
3. Generate API keys and access tokens

## Security Considerations

- Never commit your `.env` file to version control
- Use environment variables for sensitive information
- Regularly rotate your API keys and passwords
- Consider using app-specific passwords where available

## Features in Detail

### Content Generation
- AI-powered content creation using OpenAI
- Customizable prompts and content styles
- Support for different content types and formats

### Authentication
- **LinkedIn**: Secure OAuth 2.0 flow with token refresh
- **Other Platforms**: Credential-based authentication with secure storage

### Automation Logic
- Platform-specific posting logic
- Error handling and retry mechanisms
- Scheduling capabilities (if implemented)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/new-feature`)
6. Create a Pull Request

## Troubleshooting

### Common Issues

1. **LinkedIn OAuth Errors**
   - Verify your CLIENT_ID and CLIENT_SECRET
   - Check that your REDIRECT_URI matches the app configuration
   - Ensure your LinkedIn app has the necessary permissions

2. **OpenAI API Errors**
   - Verify your API key is valid and has sufficient credits
   - Check API rate limits and usage quotas

3. **Platform Authentication Failures**
   - Verify credentials are correct
   - Check for two-factor authentication requirements
   - Ensure accounts are not locked or restricted

### Debug Mode
Enable debug logging by setting environment variables or modifying the logging configuration in the code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use. Please ensure you comply with each platform's Terms of Service and API usage guidelines. Be respectful of rate limits and community guidelines when automating social media activities.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

**Note**: This automation tool should be used responsibly and in accordance with each platform's terms of service. Always respect rate limits and community guidelines.