## Cinemate – Your Movie Buddy 🎬🍿✨

A casual, witty, cinema-obsessed chatbot that recommends movies using TMDB.

### Features
- Conversational persona tailored to your favorite genres
- Weekend picks, hidden gems, and "similar to <movie>" suggestions
- Card-style output with posters via TMDB image URLs
- Easy to package as a Windows .exe

### Setup
1. Install Python 3.9+
2. Open a terminal in this folder.
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. (Optional) Put your TMDB key in a `.env` file:
```env
TMDB_API_KEY=1e3d1654e34c01d61b2b01d4dacc4bae
```

### Run
```bash
python main.py
```

### Build a Windows .exe (PyInstaller)
1. Install PyInstaller:
```bash
pip install pyinstaller
```
2. Build single-file executable:
```bash
pyinstaller --onefile --name Cinemate main.py
```
3. Your exe will be at `dist/Cinemate.exe`.

### Notes
- Data from TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.
- Images come from `https://image.tmdb.org/t/p/w500` where available.
