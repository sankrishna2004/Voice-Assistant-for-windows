import speech_recognition as sr
import pyttsx3
import os
import subprocess
import pywhatkit
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
import librosa
import sounddevice as sd
from scipy.io.wavfile import write

# Paths for models and audio files
MODEL_FILE = "F:/python/.vscode/voice/svm_speaker_model.pkl"
SCALER_FILE = "F:/python/.vscode/voice/scaler.pkl"
AUDIO_FILE = "F:/python/.vscode/voice/bhavith1.wav"  # Authorized voice file

# Set the correct voice password
VOICE_PASSWORD = "hello ak"

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Dictionary of applications and their paths
apps = {
    "whatsapp": "start whatsapp:",
    "chrome": "start chrome",
    "firefox": "start firefox",
    "notepad": "notepad",
    "command prompt": "cmd",
    "file explorer": "explorer",
    "calculator": "calc",
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
    "spotify": r"C:\Users\YourUsername\AppData\Roaming\Spotify\Spotify.exe",
    "zoom": r"C:\Users\YourUsername\AppData\Roaming\Zoom\bin\Zoom.exe",
    "visual studio code": r"C:\Users\YourUsername\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "telegram": r"C:\Users\YourUsername\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "edge": "start msedge",
    "paint": "mspaint",
    "task manager": "taskmgr",
    "snipping tool": "snippingtool",
    "control panel": "control",
    "settings": "start ms-settings:"
}

# Dictionary for WhatsApp contacts (replace with real phone numbers)
contacts = {
## enter your contact"#
## user: *************: phone no:
}

# Initialize voice recognition and text-to-speech functions
def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to voice command and return recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I could not understand your command.")
        return None
    except sr.RequestError:
        print("Speech recognition service is unavailable.")
        return None

def extract_mfcc(audio_path):
    """Extract MFCC features from a given audio file."""
    y, sr = librosa.load(audio_path, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc, axis=1).reshape(1, -1)

def verify_speaker(audio_path):
    """Verify if the speaker is authorized."""
    features = extract_mfcc(audio_path)
    
    # Load model and scaler
    with open(MODEL_FILE, 'rb') as f:
        model = pickle.load(f)

    with open(SCALER_FILE, 'rb') as f:
        scaler = pickle.load(f)

    features = scaler.transform(features)
    pred = model.predict(features)[0]
    
    # 1 is authorized voice label, 0 is unauthorized
    return pred == 1

def record_voice():
    """Record the voice input for verification."""
    fs = 44100  # Sample rate
    seconds = 3  # Recording duration
    print("🎙 Say your password...") 
    speak("Say your password")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    write(AUDIO_FILE, fs, recording)  # Save the recording
    print("✅ Voice recorded successfully.")

def authenticate():
    """Ask for voice password before allowing access."""
    speak("Please say your password to access the system.")
    record_voice()  # Record the voice
    print("🔍 Verifying speaker...")
    speak("Verifying speaker")
    if verify_speaker(AUDIO_FILE):
        speak("Access granted. How can I assist you?")
        return True
    else:
        speak("You are  not bhavith .")
        print("Unauthorized access attempt detected!")
        return False

def send_whatsapp_message(contact_name, message):
    """Send a WhatsApp message to a specific contact."""
    if contact_name in contacts:
        phone_number = contacts[contact_name]
        speak(f"Sending message to {contact_name}")
        print(f"Sending WhatsApp message to {contact_name} ({phone_number}): {message}")
        
        # Open WhatsApp and send the message
        pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10)
    else:
        speak("Contact not found.")

def execute_command(command):
    """Execute system commands based on voice input."""
    if "whatsapp" in command and "send a message" in command:
        speak("Who do you want to message?")
        contact_name = listen()
        if contact_name:
            speak("What is your message?")
            message = listen()
            if message:
                send_whatsapp_message(contact_name, message)
            else:
                speak("Message not understood.")
        else:
            speak("Contact name not understood.")
    elif "whatsapp" in command:  # If user says only "open WhatsApp"
        speak("Opening WhatsApp")
        os.system("start whatsapp:")
    elif "exit" in command or "stop" in command:
        speak("Goodbye! Have a great day.")
        print("Exiting...")
        exit()  # This will properly exit the program
    else:
        for app in apps:
            if app in command:
                speak(f"Opening {app}")
                if apps[app].startswith("start") or apps[app] in ["notepad", "cmd", "explorer", "calc"]:
                    os.system(apps[app])
                else:
                    subprocess.Popen([apps[app]], shell=True)
                return

        speak("Application not found. Please try again.")

# Main program execution
if __name__ == "__main__":
    if authenticate():
        while True:  # Keep running in a loop
            command = listen()
            if command:
                execute_command(command)