import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# You can override this with the TMDB_API_KEY env var if you want
TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "1e3d1654e34c01d61b2b01d4dacc4bae")

TMDB_API_BASE_URL: str = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"

# Cinemate persona constants
CINEMATE_NAME: str = "Cinemate"
WELCOME_PROMPT: str = (
	"Hey there! I'm Cinemate, your movie bestie 🍿✨\n"
	"Before we dive into the good stuff, what are your favorite genres?\n"
	"Try a few like: Action, Comedy, Romance, Thriller, Sci-Fi, Drama, Horror, Animation, Mystery, Fantasy."
)

# Default number of recommendations to show in a single response
DEFAULT_RECOMMENDATIONS_COUNT: int = 5
