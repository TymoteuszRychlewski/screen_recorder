Screen Recorder for Linux / Rejestrator ekranu dla Linuksa

A simple and user-friendly screen recording application for Linux with audio support and a graphical interface. 
Prosta i przyjazna aplikacja do nagrywania ekranu dla Linuksa z obsługą dźwięku i interfejsem graficznym.

---

Features / Funkcje

- Capture modes: entire screen, specific window, or selected area 
  Tryby nagrywania: cały ekran, konkretne okno lub wybrany obszar

- Record microphone and/or system audio 
  Nagrywaj mikrofon i/lub dźwięk systemowy

- Adjustable FPS, delay, duration, and format (`mp4`, `webm`) 
  Regulowany FPS, opóźnienie, czas trwania i format wyjściowy

- Auto-stop with notification, manual stop, timestamped filenames 
  Automatyczne zakończenie z powiadomieniem, ręczne zatrzymanie, nazwy z datą

- Saves user settings between sessions 
  Zapisuje ustawienia użytkownika między sesjami

---

Requirements / Wymagania

- `python3`, `python3-pyqt5`
- `ffmpeg`
- `slop`
- `wmctrl`
- `x11-utils` (for `xwininfo`)
- `pulseaudio` (`pactl`)

---

Installation / Instalacja

Option 1: Install from `.deb` package / Zainstaluj z pakietu `.deb`

sudo dpkg -i screen-recorder.deb

Option 2: Run from source / Uruchom z kodu źródłowego

sudo apt install ffmpeg slop wmctrl x11-utils pulseaudio python3 python3-pyqt5
git clone https://github.com/your-username/screen-recorder.git
cd screen-recorder
python3 main.py

This project is licensed under the MIT License.
Ten projekt jest objęty licencją MIT.

Created by Tymoteusz Rychlewski as an engineering thesis project.
Stworzony przez Tymoteusza Rychlewskiego jako projekt pracy inżynierskiej.
