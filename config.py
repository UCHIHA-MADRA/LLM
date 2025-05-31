# Model Configuration
MODEL_NAME = "microsoft/CodeBERT-base"  # Better for code tasks
CODE_MODEL_NAME = "Salesforce/codegen-350M-mono"  # Specialized for code generation

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = "Ov23liVPi4syOCSMQUrC"
GITHUB_CLIENT_SECRET = "0558a6987596c3238066c8d97f9e9d4ce083c471"
GITHUB_OAUTH_DOMAIN = "localhost"  # Just the domain, no protocol or port
APPLICATION_WEBSITE = "http://localhost:3000"  # Full URL for the homepage
APPLICATION_NAME = "LLM"
APPLICATION_DESCRIPTION = "Your app description"

# Stack Exchange API Configuration
STACKEXCHANGE_CLIENT_ID = "33355"
STACKEXCHANGE_CLIENT_SECRET = "Ij72FYcKzkCBrekBm93uhg(("
STACKEXCHANGE_KEY = "rl_wXQbb16qcMbMuvnySQ3frEioa"
STACKEXCHANGE_OAUTH_DOMAIN = "localhost"
STACKEXCHANGE_DESCRIPTION = "A personal tool for testing the Stack Overflow API."

# Existing configuration
GITHUB_API_TOKEN = "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"
CHROMA_DB_DIR = "db/"
STACKOVERFLOW_API_KEY = "rl_wXQbb16qcMbMuvnySQ3frEioa"  # Updated with the Stack Exchange API key
TRAINING_DATA_DIR = "training_data/"
MAX_REPOS_TO_SCRAPE = 1000
MAX_SO_QUESTIONS = 5000

# Code Analysis Settings
SUPPORTED_LANGUAGES = ["python", "javascript", "java", "cpp", "go", "rust"]
MAX_CODE_LENGTH = 2048
BATCH_SIZE = 16
LEARNING_RATE = 5e-5
