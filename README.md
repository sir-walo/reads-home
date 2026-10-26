# READS Home Reading (offline APK)

Take-home reading intervention tool. No internet, no server: stories are in `stories.json`,
metrics are computed on the phone, speech uses Android's built-in recognizer.

## Build on Windows (Buildozer needs Linux -> use WSL2)
1. PowerShell (admin): `wsl --install -d Ubuntu`, restart.
2. In Ubuntu: 
   sudo apt update && sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev
3. Copy the project into Linux (faster/safer than /mnt/c):
   cp -r /mnt/c/PR_Apk ~/PR_Apk && cd ~/PR_Apk
4. python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
5. Test UI on desktop first (optional): python main.py
6. buildozer android debug   (first build downloads SDK/NDK, 20-40 min)
7. APK appears in ./bin/ -> copy to C:\PR_Apk\bin

## No-WSL option
Push to GitHub, open Actions > "Build APK" > Run workflow, download the APK artifact.

## Student phone setup (important for offline speech)
Settings > Google > Voice > Offline speech recognition: download English (and Filipino if available).
Install the APK (allow "unknown sources"), allow microphone.

## Adding stories
Edit stories.json: {"id": 3, "grade": 5, "category": "English", "title": "...", "content": "..."}
Progress is saved on the phone in progress.jsonl (app's private storage).
