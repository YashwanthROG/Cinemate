from typing import Dict, List, Optional

from config import (
	CINEMATE_NAME,
	DEFAULT_RECOMMENDATIONS_COUNT,
	WELCOME_PROMPT,
)
from tmdb_client import TMDBClient, format_card


GENRE_KEYWORDS = {
	"action": "Action",
	"comedy": "Comedy",
	"romance": "Romance",
	"thriller": "Thriller",
	"sci-fi": "Science Fiction",
	"science fiction": "Science Fiction",
	"drama": "Drama",
	"horror": "Horror",
	"animation": "Animation",
	"mystery": "Mystery",
	"fantasy": "Fantasy",
}


class CinemateBot:
	"""Conversational movie buddy with TMDB-powered recommendations."""

	def __init__(self, tmdb: Optional[TMDBClient] = None) -> None:
		self.tmdb = tmdb or TMDBClient()
		self.user_genres: List[str] = []
		self._asked_for_genres: bool = False

	def opening(self) -> str:
		self._asked_for_genres = True
		return WELCOME_PROMPT

	def _extract_genres(self, text: str) -> List[str]:
		text_lower = text.lower()
		found = []
		for key, nice in GENRE_KEYWORDS.items():
			if key in text_lower:
				found.append(nice)
		return list(dict.fromkeys(found))

	def _ensure_genres(self, user_text: str) -> Optional[str]:
		if not self.user_genres:
			genres = self._extract_genres(user_text)
			if genres:
				self.user_genres = genres
				return f"Nice picks! I’ll keep {', '.join(self.user_genres)} at the top of my list 🎬"
			return None
		return None

	def _is_weekend_intent(self, text: str) -> bool:
		text = text.lower()
		return any(w in text for w in ["weekend", "tonight", "friday", "saturday", "sunday", "binge"])

	def _is_hidden_gems_intent(self, text: str) -> bool:
		text = text.lower()
		return "hidden" in text or "underrated" in text or "gems" in text

	def _is_similar_intent(self, text: str) -> Optional[str]:
		# naive pattern: "like <movie>" or "similar to <movie>"
		text = text.lower()
		trigger_phrases = ["like ", "similar to ", "more like "]
		for phrase in trigger_phrases:
			if phrase in text:
				idx = text.find(phrase) + len(phrase)
				candidate = text[idx:].strip().strip(".? !")
				if candidate:
					return candidate
		return None

	def reply(self, user_text: str, count: int = DEFAULT_RECOMMENDATIONS_COUNT) -> str:
		# keep conversations on movies
		if not any(k in user_text.lower() for k in ["movie", "film", "series", "show", "actor", "director", "tv", "cinema", "recommend", "watch", "like", "similar", "trending", "hidden", "weekend", "tonight"]):
			return (
				"I’m all about the movies, bestie 🎬 Let’s chat films, shows, actors, soundtracks—"
				"tell me a genre you love or ask for a recommendation!"
			)

		ack = self._ensure_genres(user_text)

		# Similar-to intent
		similar_to = self._is_similar_intent(user_text)
		if similar_to:
			return self._recommend_similar(similar_to, count)

		# Hidden gems intent
		if self._is_hidden_gems_intent(user_text):
			return self._hidden_gems(count)

		# Weekend picks intent
		if self._is_weekend_intent(user_text):
			return self._weekend_picks(count)

		# General recommend flow (prefer user genres if known)
		if self.user_genres:
			return (ack + "\n\n" if ack else "") + self._recommend_by_genres(self.user_genres, count)

		# Fallback: trending
		cards = self._format_cards(self.tmdb.trending(page=1)[:count])
		return (ack + "\n\n" if ack else "") + (
			"Hot right now 🔥 Here’s what people are buzzing about:\n\n" + cards +
			"\n\nWant more like this? Should I find similar ones from another language/era?"
		)

	def _genre_names_to_ids(self, names: List[str]) -> List[int]:
		genres_map = self.tmdb.get_genres()
		rev = {v.lower(): k for k, v in genres_map.items()}
		ids = []
		for name in names:
			gid = rev.get(name.lower())
			if gid is not None:
				ids.append(gid)
		return ids

	def _format_cards(self, movies: List[Dict]) -> str:
		return "\n\n".join(format_card(m) for m in movies)

	def _recommend_by_genres(self, genres: List[str], count: int) -> str:
		ids = self._genre_names_to_ids(genres)
		if not ids:
			cards = self._format_cards(self.tmdb.trending(page=1)[:count])
			return (
				"Couldn’t match those genres perfectly, but here’s what’s hot this week 🔥\n\n" +
				cards +
				"\n\nWant more like this?"
			)
		movies = self.tmdb.discover_by_genres(ids, page=1)
		cards = self._format_cards(movies[:count])
		return (
			f"Handpicked {', '.join(genres)} picks just for you 🍿:\n\n" +
			cards +
			"\n\nWant more like this? Should I find similar ones from another language/era?"
		)

	def _hidden_gems(self, count: int) -> str:
		movies = self.tmdb.hidden_gems(page=1)
		cards = self._format_cards(movies[:count])
		return (
			"Hidden gems time ✨ These may have flown under the radar, but they sparkle:\n\n" +
			cards +
			"\n\nSome reviews weren’t very positive… but hey, taste is personal, and you might still enjoy it if it fits your vibe ✨. Want more?"
		)

	def _weekend_picks(self, count: int) -> str:
		base = self.tmdb.trending(page=1)
		cards = self._format_cards(base[:count])
		return (
			"Weekend picks coming right up 🎉 Cozy blanket optional, snacks mandatory:\n\n" +
			cards +
			"\n\nWant me to tailor these tighter to a genre or era?"
		)

	def _recommend_similar(self, title_query: str, count: int) -> str:
		search = self.tmdb.search_movie(title_query)
		if not search:
			return (
				f"I couldn’t find ‘{title_query}’. Maybe try the exact title or another one?"
			)
		movie = search[0]
		movie_id = movie.get("id")
		similar = self.tmdb.get_similar(movie_id)
		if not similar:
			recs = self.tmdb.get_recommendations(movie_id)
			similar = recs
		cards = self._format_cards(similar[:count])
		return (
			f"If you liked ‘{movie.get('title', title_query)}’, you might vibe with these 🎬:\n\n" +
			cards +
			"\n\nWant more like this?"
		)
