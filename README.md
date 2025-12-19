# 🎵 MuLyCue

**Music Lyrics & Chords Cue System**

A powerful desktop application for synchronized lyrics, chords, and timing display designed for live music performances. MuLyCue helps musicians stay in sync with real-time lyrics and chord progression display, BPM tracking, and on-the-fly transposition.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](version.json)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/GitHub-serkankas%2FMuLyCue-blue?logo=github)](https://github.com/serkankas/MuLyCue)

**Designed By:** Serkan KAS  
**Contact:** serkankas98@gmail.com  
**AI Assistant:** Claude Sonnet 4.5 (via Cursor)  
**Development:** Codes and documentation prepared with assistance from Cursor AI

---

## ✨ Features

### 🎨 Professional Panel System
- **OBS-Style Interface**: Drag-and-drop panels like professional streaming software
- **8 Panel Types**: Lyrics, Chords, BPM, Beat Counter, Section, Timeline, Transpose, **Setlist**
- **Multi-Monitor Support**: Pop out panels to separate windows
- **Layout Presets**: Quick layouts for different roles (Vocalist, Guitarist, Drummer)
- **Custom Layouts**: Save and share your own layouts
- **Real-Time Sync**: All windows stay synchronized
- **Boundary Constraints**: Panels stay within viewport, never go off-screen
- **24×24 Grid Snap**: Optional grid system for precise alignment

### 📋 Setlist/Queue System
- **Professional Setlist Management**: Create and manage playlists for gigs and shows
- **Setlist Manager UI**: Full-featured interface for creating and editing setlists
- **Auto-Advance**: Automatically load next song when current finishes
- **Configurable Gaps**: Set time between songs (0-60 seconds) with countdown
- **Manual Navigation**: Skip forward/backward or jump to any song
- **Shuffle & Loop**: Shuffle playback order or loop entire setlist
- **Progress Tracking**: Track elapsed time, remaining songs, and overall progress
- **Performance Notes**: Add notes per song (capo, tuning, etc.)
- **Per-Song Overrides**: Override transpose for individual songs
- **Save/Load Setlists**: Save setlists for different gigs and venues (.mls format)
- **Tags & Organization**: Organize setlists by venue, genre, or event type
- **Live Panel Integration**: Setlist panel in player shows current song and progress
- **One-Click Load**: Load setlist directly to player from manager

### 🎼 Editor Mode
- **Import Audio Files**: Support for MP3, OGG, and WAV formats
- **Lyrics Management**: Paste and organize lyrics into sections (Verse, Chorus, Bridge, etc.)
- **Time Synchronization**: Mark exact timing for each word or phrase
- **Chord Notation**: Add chords with support for complex notation (m7, maj7, sus4, etc.)
- **Visual Timeline**: See your song structure at a glance
- **Auto-Sync** (Coming Soon): Automatic beat detection and timing

### ▶️ Player Mode (Professional Panel System)
- **Multi-Window Panel System**: OBS Studio/DAW-style drag-and-drop panels
- **Modular Panels**: Lyrics, Chords, BPM, Beat Counter, Section, Timeline, Transpose
- **Drag & Drop**: Freely position panels anywhere on screen
- **Resizable Panels**: Drag corners/edges to resize
- **Pop-Out Windows**: Detach panels to separate windows (perfect for dual/triple monitors)
- **Layout Presets**: Vocalist, Guitarist, Drummer, Minimal, Fullscreen
- **Save/Load Layouts**: Custom layouts with export/import (JSON)
- **Real-Time Sync**: All panels sync across multiple windows via BroadcastChannel
- **Live Transpose**: Change key on-the-fly without stopping playback
- **Professional Grade**: Designed for live performances

### 🎹 Advanced Features
- **Smart Transposition**: Transpose chords while preserving quality (m7 stays m7)
- **Slash Chords**: Full support for bass note notation (C/G, Am/E)
- **Sharp/Flat Notation**: Choose your preferred notation style
- **Capo Support**: Automatic transposition for capo positions
- **Section Navigation**: Jump between song sections easily
- **Song Library**: Manage and organize your song collection

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/MuLyCue.git
cd MuLyCue
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python src/launcher.py
```

Or run in development mode:
```bash
# Start backend only
python -m uvicorn src.backend.main:app --reload

# Then open browser to http://localhost:8000
```

---

## 📦 Building Executables

Build standalone executables for distribution:

```bash
# Build single-file executable
python build.py

# Build as directory (faster for development)
python build.py --dir

# Clean previous builds first
python build.py --clean
```

Executables will be created in the `dist/` directory.

---

## 🎯 Usage Guide

### Creating Your First Song

1. **Launch MuLyCue** and select **Editor Mode**
2. **Fill in song metadata**:
   - Title, Artist, Album
   - Key, BPM, Time Signature
   - Upload audio file (optional)

3. **Add sections**:
   - Click "Add Section"
   - Name it (Intro, Verse 1, Chorus, etc.)
   - Set start and end times

4. **Add lyrics and chords**:
   - Click "Add Entry" in a section
   - Type the word/phrase
   - Add chord notation
   - Mark timing using audio player

5. **Save your song**:
   - Click "Save" button
   - Song is saved as `.mlc` file in `data/songs/`

### Playing a Song

1. **Select Player Mode** from main menu
2. **Choose a song** from the library
3. **Control playback**:
   - Play/Pause: Space bar or ▶️ button
   - Seek: Click on progress bar
   - Transpose: Use +/- buttons
   - Volume: Adjust slider

4. **Customize display**:
   - Click ⚙️ for settings
   - Adjust font size, theme, display mode
   - Toggle chords/beat indicator

---

## 📁 Project Structure

```
MuLyCue/
├── src/
│   ├── backend/              # FastAPI backend
│   │   ├── models/           # Data models (Chord, Song, MLC)
│   │   ├── core/             # Core engines (Audio, Sync, WebSocket)
│   │   ├── api/              # REST & WebSocket endpoints
│   │   ├── utils/            # Utility functions
│   │   └── main.py           # FastAPI app entry
│   ├── frontend/             # Web frontend
│   │   ├── index.html        # Landing page
│   │   ├── editor.html       # Song editor
│   │   ├── player-panels.html # Professional panel-based player
│   │   ├── player-window.html # Detached panel window
│   │   ├── test-panels.html  # Panel system test page
│   │   ├── css/              # Stylesheets
│   │   └── js/               # JavaScript modules
│   └── launcher.py           # Desktop app launcher
├── data/
│   └── songs/                # Song files (.mlc + audio)
├── tests/                    # Unit tests
├── examples/                 # Example songs
├── build.py                  # Build script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🎼 .MLC File Format

MuLyCue uses a JSON-based `.mlc` format for song data:

```json
{
  "version": "1.0.0",
  "meta": {
    "title": "Song Title",
    "artist": "Artist Name",
    "bpm": 120,
    "key": "C",
    "time_signature": "4/4",
    "duration": 180.0,
    "audio_file": "song.mp3"
  },
  "sections": [
    {
      "name": "Verse 1",
      "order": 1,
      "start_time": 0.0,
      "end_time": 20.0,
      "entries": [
        {
          "word": "Hello",
          "start_time": 0.0,
          "end_time": 1.0,
          "chords": "C"
        }
      ]
    }
  ]
}
```

See `examples/sample_song.mlc` for a complete example.

---

## 🔧 API Documentation

### REST Endpoints

- `GET /api/songs` - List all songs
- `GET /api/songs/{id}` - Get song details
- `POST /api/songs` - Upload new song
- `PUT /api/songs/{id}` - Update song
- `DELETE /api/songs/{id}` - Delete song
- `POST /api/songs/{id}/transpose` - Transpose song
- `POST /api/playback/play` - Start playback
- `POST /api/playback/pause` - Pause playback
- `POST /api/playback/stop` - Stop playback
- `POST /api/playback/seek` - Seek to position

### WebSocket Endpoint

Connect to `ws://localhost:8000/ws` for real-time updates:

**Received Messages:**
- `position_update` - Current playback position
- `entry_change` - Current word/chord
- `section_change` - Section change
- `beat_tick` - Beat events (1-4)
- `playback_state` - Play/pause/stop
- `song_loaded` - New song loaded

**Send Messages:**
- `{"type": "play"}` - Start playback
- `{"type": "pause"}` - Pause playback
- `{"type": "seek", "position": 10.5}` - Seek to position

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chord.py

# Run with coverage
pytest --cov=src tests/
```

---

## 🛠️ Development

### Tech Stack

- **Backend**: FastAPI + uvicorn (WebSocket support)
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Desktop**: PyWebView (native window wrapper)
- **Audio**: pygame.mixer
- **Build**: PyInstaller

### Setting Up Development Environment

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run in development mode:
```bash
python -m uvicorn src.backend.main:app --reload
```

4. Access at `http://localhost:8000`

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all functions
- Add docstrings to all classes and functions
- Keep functions focused and modular

---

## 🎹 Chord Notation Guide

MuLyCue supports comprehensive chord notation:

### Basic Chords
- Major: `C`, `D`, `G`
- Minor: `Am`, `Dm`, `Em`
- Diminished: `Cdim`, `Bdim`
- Augmented: `Caug`, `Gaug`

### Extended Chords
- Seventh: `C7`, `G7`, `Am7`
- Major Seventh: `Cmaj7`, `Fmaj7`
- Minor Seventh: `Am7`, `Dm7`
- Diminished Seventh: `Cdim7`, `Bdim7`
- Half-Diminished: `Cm7b5`, `Bm7b5`

### Suspended & Added
- Suspended: `Csus2`, `Dsus4`
- Added: `Cadd9`, `Gadd11`
- Sixth: `C6`, `Am6`

### Slash Chords (Bass Notes)
- `C/G` - C chord with G in bass
- `Am/E` - A minor with E in bass
- `F/C` - F chord with C in bass

---

## 🐛 Known Limitations (v0.1.0)

### Current Limitations
- **Seeking:** Audio seeking is not yet supported with pygame backend. Will be implemented in v2.0 with VLC backend.
- **Audio Formats:** Currently supports MP3, OGG, WAV. Other formats may require additional codecs.
- **Duration Detection:** Uses mutagen library for MP3 duration calculation.
- **Waveform Visualization:** Not yet implemented.
- **Auto-sync:** Not yet implemented.
- **Single Audio Track:** Only one audio track per song.
- **No Cloud Sync:** Local storage only.

### Workarounds
- **For seeking:** Use stop/play to restart from beginning, or wait for v2.0
- **For other formats:** Convert to MP3/OGG using ffmpeg or similar tools

---

## 🗺️ Roadmap

### Version 0.2.0 (Next Release)
- [ ] **Audio seeking support** (python-vlc backend)
- [ ] **Setlist Manager UI** (frontend for setlist creation/editing)
- [ ] Waveform visualization in editor
- [ ] Auto BPM detection
- [ ] Chord diagram display
- [ ] Export to PDF/print

### Version 0.3.0
- [ ] ML-based auto-sync
- [ ] Multiple audio tracks
- [ ] Setlist statistics and analytics
- [ ] Cloud backup for setlists

### Version 0.4.0
- [ ] **MIDI controller support** (footswitch for setlist navigation)
- [ ] Chord diagrams (guitar, piano, ukulele)
- [ ] Backing track mixer

### Version 1.0.0
- [ ] Multi-user collaboration
- [ ] Cloud sync
- [ ] Mobile companion app
- [ ] Plugin system

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Write tests for new features
- Update documentation
- Follow existing code style
- Keep commits atomic and well-described

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by the needs of live performers and worship teams
- Built with modern web technologies and Python
- Thanks to all contributors and testers

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/MuLyCue/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/MuLyCue/discussions)
- **Email**: support@mulycue.com

---

## 📸 Screenshots

### Main Menu
![Main Menu](docs/screenshots/main-menu.png)

### Editor Mode
![Editor Mode](docs/screenshots/editor.png)

### Player Mode
![Player Mode](docs/screenshots/player.png)

---

## 👨‍💻 Credits & Acknowledgments

### **Project Creator**
**Serkan KAS**  
📧 serkankas98@gmail.com  
🔗 [GitHub: @serkankas](https://github.com/serkankas)

### **Development**
- **AI Assistant**: Claude Sonnet 4.5 (Anthropic)
- **Development Environment**: Cursor AI Editor
- **Methodology**: AI-assisted development with human oversight and design

### **Technology Stack**
- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Audio**: pygame.mixer, mutagen
- **Desktop**: PyWebView
- **Real-time**: WebSockets, BroadcastChannel API

### **Special Thanks**
- Anthropic for Claude Sonnet 4.5
- Cursor team for the amazing AI-powered development environment
- Open source community for the libraries and tools used

---

## 🎵 Made with ❤️ for Musicians

MuLyCue is designed by musicians, for musicians. Whether you're performing live, practicing at home, or leading worship, MuLyCue helps you stay in sync and focused on your performance.

**Repository**: [github.com/serkankas/MuLyCue](https://github.com/serkankas/MuLyCue)

**Happy Playing! 🎸🎹🎤**

