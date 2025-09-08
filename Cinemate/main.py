# main.py
import sys
from typing import Optional
from colorama import Fore, Style, init as colorama_init

from config import CINEMATE_NAME, WELCOME_PROMPT
from movie_handler import handle_user_message


def print_header() -> None:
    print(Fore.MAGENTA + f"{CINEMATE_NAME} · Your Movie Buddy 🎬🍿✨" + Style.RESET_ALL)
    print("Type 'exit' to quit. Ask for weekend picks, hidden gems, or say 'similar to Inception'.")
    print()


def main(argv: Optional[list] = None) -> int:
    colorama_init(autoreset=True)
    print_header()
    print(Fore.CYAN + WELCOME_PROMPT + Style.RESET_ALL)

    while True:
        try:
            user = input(Fore.YELLOW + "You: " + Style.RESET_ALL).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit", "bye"}:
            break

        # 🔹 Use our LLM + TMDB handler
        reply = handle_user_message(user)
        print(Fore.GREEN + f"{CINEMATE_NAME}: " + Style.RESET_ALL + reply)

    print(Fore.MAGENTA + "Catch you later—happy watching! ✨" + Style.RESET_ALL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
