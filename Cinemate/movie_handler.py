# movie_handler.py
import json
from ollama_client import query_ollama  # Your Ollama client function
from tmdb_client import search_tmdb  # Your TMDB search function
from config import DEFAULT_RECOMMENDATIONS_COUNT


# Optional: existing rule-based logic
def try_rule_based_logic(user_text: str) -> str:
    """Return a reply if it matches rule-based logic, else 'NO_MATCH'."""
    user_text = user_text.lower()
    if "hello" in user_text or "hi" in user_text:
        return "Hey there! Ready for some movie magic? 🍿"
    if "weekend" in user_text:
        return "Looking for weekend picks? I got you! 🎬"
    return "NO_MATCH"


def make_movie_reply(movies: list) -> str:
    """Format a list of movies into a friendly reply."""
    if not movies:
        return "Oops, no movies found. Try another genre or title!"
    reply = "Here are some movies I think you'll enjoy:\n"
    for m in movies[:DEFAULT_RECOMMENDATIONS_COUNT]:  # use config value
        reply += f"- {m.get('title', 'Unknown')} ({m.get('release_date', '')[:4]})\n"
    return reply.strip()


def handle_user_message(user_text: str) -> str:
    # 1) Try rule-based first
    rule_reply = try_rule_based_logic(user_text)
    if rule_reply != "NO_MATCH":
        return rule_reply

    # 2) LLM prompt
    prompt = f"""
You are Cinemate, a sweet, chatty movie-buff friend. When given the user's message,
output a JSON object ONLY with keys: intent, genre, query, reply.
- intent: one of ["recommend","info","search","chat","unknown"]
- genre: optional (e.g., "romance")
- query: optional text to search TMDB (e.g., "movies like interstellar")
- reply: a short friendly phrase to show the user if no movie is found.

User message: {user_text}
"""
    llm_text = query_ollama(prompt)

    try:
        parsed = json.loads(llm_text)
    except Exception:
        return llm_text or "Sorry, I couldn't understand that."

    intent = parsed.get("intent")
    if intent == "recommend":
        movies = search_tmdb(parsed.get("query") or "", genre=parsed.get("genre"))
        if movies:
            return make_movie_reply(movies)
        else:
            return parsed.get("reply", "I couldn't find any movies like that. Want to try another genre?")
    elif intent == "chat":
        return parsed.get("reply", "Nice! Tell me more about what you like in movies.")
    else:
        return parsed.get("reply", "Hm, I didn't get that. Can you rephrase?")
