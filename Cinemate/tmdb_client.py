import time
from typing import Dict, List, Optional

import requests

from config import TMDB_API_BASE_URL, TMDB_API_KEY, TMDB_IMAGE_BASE_URL


class TMDBClient:
	"""Lightweight TMDB API client for fetching movies and metadata."""

	def __init__(self, api_key: Optional[str] = None, request_timeout_seconds: int = 12) -> None:
		self.api_key: str = api_key or TMDB_API_KEY
		self.request_timeout_seconds: int = request_timeout_seconds
		self._genre_cache_timestamp: float = 0.0
		self._genres: Dict[int, str] = {}

	def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
		if params is None:
			params = {}
		params["api_key"] = self.api_key
		url = f"{TMDB_API_BASE_URL}{path}"
		response = requests.get(url, params=params, timeout=self.request_timeout_seconds)
		response.raise_for_status()
		return response.json()

	def get_genres(self) -> Dict[int, str]:
		# Cache genres for 24 hours to avoid repeated calls
		if self._genres and (time.time() - self._genre_cache_timestamp) < 24 * 3600:
			return self._genres
		data = self._get("/genre/movie/list", {"language": "en-US"})
		genres = {g["id"]: g["name"] for g in data.get("genres", [])}
		self._genres = genres
		self._genre_cache_timestamp = time.time()
		return genres

	def search_movie(self, query: str, page: int = 1) -> List[Dict]:
		data = self._get("/search/movie", {"query": query, "language": "en-US", "page": str(page), "include_adult": "false"})
		return data.get("results", [])

	def trending(self, page: int = 1) -> List[Dict]:
		data = self._get("/trending/movie/week", {"language": "en-US", "page": str(page)})
		return data.get("results", [])

	def discover_by_genres(self, genre_ids: List[int], page: int = 1, sort_by: str = "popularity.desc") -> List[Dict]:
		params = {
			"with_genres": ",".join(str(g) for g in genre_ids),
			"language": "en-US",
			"sort_by": sort_by,
			"page": str(page),
			"include_adult": "false",
		}
		data = self._get("/discover/movie", params)
		return data.get("results", [])

	def hidden_gems(self, page: int = 1) -> List[Dict]:
		# Heuristic: highly rated but not super popular
		params = {
			"sort_by": "vote_average.desc",
			"vote_count.gte": "300",
			"language": "en-US",
			"page": str(page),
			"include_adult": "false",
		}
		data = self._get("/discover/movie", params)
		return data.get("results", [])

	def get_recommendations(self, movie_id: int, page: int = 1) -> List[Dict]:
		data = self._get(f"/movie/{movie_id}/recommendations", {"language": "en-US", "page": str(page)})
		return data.get("results", [])

	def get_similar(self, movie_id: int, page: int = 1) -> List[Dict]:
		data = self._get(f"/movie/{movie_id}/similar", {"language": "en-US", "page": str(page)})
		return data.get("results", [])

	def get_movie_details(self, movie_id: int) -> Dict:
		return self._get(f"/movie/{movie_id}", {"language": "en-US"})

	@staticmethod
	def poster_url(path: Optional[str]) -> Optional[str]:
		if not path:
			return None
		return f"{TMDB_IMAGE_BASE_URL}{path}"

# Create a client instance
_tmdb_client = TMDBClient()

def search_tmdb(query: str, genre: str = None) -> list:
    """
    Wrapper for movie_handler.py.
    - query: search text
    - genre: optional genre name
    Returns a list of movie dicts.
    """
    results = []
    if query:
        results = _tmdb_client.search_movie(query)
    elif genre:
        # map genre name to id
        genres = _tmdb_client.get_genres()
        genre_ids = [gid for gid, name in genres.items() if name.lower() == genre.lower()]
        if genre_ids:
            results = _tmdb_client.discover_by_genres(genre_ids)
    return results


def format_card(movie: Dict) -> str:
	"""Return a card-like string per the UI format."""
	title = movie.get("title") or movie.get("name") or "Unknown"
	year = (movie.get("release_date") or "?")[:4]
	genres = movie.get("genre_ids", [])
	vote = movie.get("vote_average")
	poster_path = movie.get("poster_path")
	poster = TMDBClient.poster_url(poster_path) or "[Poster unavailable]"

	# Genre names are not in the search results; leave ids or blank.
	genre_text = ", ".join(str(g) for g in genres) if genres else "Unknown"
	hook = (movie.get("overview") or "A little mystery makes it fun.").strip()
	if len(hook) > 120:
		hook = hook[:117] + "..."

	lines = [
		f"🎬 {title} ({year})",
		f"Genre: {genre_text}",
		f"⭐ Rating: {vote:.1f}/10" if isinstance(vote, (int, float)) else "⭐ Rating: N/A",
		f"📝 Hook: {hook}",
		f"Poster: {poster}",
	]
	return "\n".join(lines)
