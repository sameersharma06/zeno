# agents/automation_agent.py
import subprocess
from core.memory import log_event


SAFE_APPS = [
    "Safari", "Google Chrome", "Firefox", "Brave Browser",
    "Visual Studio Code", "Terminal", "iTerm", "Cursor",
    "Finder", "Notes", "Calendar", "Reminders",
    "Spotify", "Music", "VLC", "QuickTime Player",
    "Slack", "Zoom", "Telegram", "WhatsApp", "Discord",
    "FaceTime", "Messages", "Mail",
    "ChatGPT", "Atlas",
    "Notion", "Obsidian",
    "Photos", "Photo Booth", "App Store",
    "System Preferences", "Activity Monitor", "Calculator", "Preview",
    "Xcode", "GitHub Desktop", "Postman", "Docker",
    "Figma", "Canva",
]

APP_ALIASES = {
    # Chrome
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",

    # Brave
    "brave": "Brave Browser",
    "brave browser": "Brave Browser",

    # VS Code
    "vs code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "code": "Visual Studio Code",

    # Browsers
    "safari": "Safari",
    "firefox": "Firefox",

    # Communication
    "slack": "Slack",
    "zoom": "Zoom",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "discord": "Discord",
    "facetime": "FaceTime",
    "messages": "Messages",
    "mail": "Mail",

    # AI tools
    "chatgpt": "ChatGPT",
    "atlas": "Atlas",

    # Productivity
    "notion": "Notion",
    "obsidian": "Obsidian",
    "notes": "Notes",
    "calendar": "Calendar",
    "reminders": "Reminders",
    "finder": "Finder",
    "terminal": "Terminal",
    "iterm": "iTerm",

    # Media
    "spotify": "Spotify",
    "music": "Music",
    "vlc": "VLC",
    "quicktime": "QuickTime Player",
    "quicktime player": "QuickTime Player",

    # Apple apps
    "photos": "Photos",
    "photobooth": "Photo Booth",
    "photo booth": "Photo Booth",
    "appstore": "App Store",
    "app store": "App Store",
    "system preferences": "System Preferences",
    "settings": "System Preferences",
    "activity monitor": "Activity Monitor",
    "calculator": "Calculator",
    "preview": "Preview",

    # Dev tools
    "xcode": "Xcode",
    "github desktop": "GitHub Desktop",
    "postman": "Postman",
    "docker": "Docker",
    "cursor": "Cursor",

    # Creative
    "figma": "Figma",
    "canva": "Canva",
}


def run_applescript(script: str) -> str:
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() or "Done."
    except subprocess.TimeoutExpired:
        return "Action timed out."
    except Exception as e:
        return f"Automation error: {str(e)}"


def open_app(app_name: str) -> str:
    safe = any(s.lower() == app_name.lower() for s in SAFE_APPS)
    if not safe:
        return f"'{app_name}' is not in the safe apps list."
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        log_event("automation", f"opened {app_name}")
        return f"Opened {app_name}."
    except subprocess.CalledProcessError:
        return f"Could not open {app_name}. App may not be installed."


def show_notification(title: str, message: str) -> str:
    script = f'display notification "{message}" with title "{title}"'
    return run_applescript(script)


def run(user_input: str) -> str:
    text = user_input.lower()

    # Open app
    if "open" in text or "launch" in text or "start" in text:
        for alias, real_name in APP_ALIASES.items():
            if alias in text:
                return open_app(real_name)
        return f"Which app? I can open: {', '.join(sorted(set(APP_ALIASES.values())))}"

    # Notification
    if "notify" in text or "notification" in text or "remind" in text:
        return show_notification("SAMEER AI", user_input)

    return "Automation: Try 'open Chrome', 'open VS Code', 'open Spotify', or 'remind me to take a break'."