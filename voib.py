import os
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import librosa
import pickle
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

# Paths
AUTH_DIR = r"C:\auth"  # Raw string
UNAUTH_DIR = r"C:\unauther"
MODEL_PATH = r"C:\model"
SCALER_PATH = r"C:\model\scaler.pkl"

fs = 44100  # Sample rate
seconds = 3  # Recording duration
num_samples = 5  # Number of recordings

def record_voice(filename):
    """Records voice and saves it as a WAV file."""
    print(f"🎙 Recording {filename}... Speak now!")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, recording)
    print(f"✅ Saved: {filename}")

# Step 1: Record Your Voice
os.makedirs(AUTH_DIR, exist_ok=True)
for i in range(1, num_samples + 1):
    record_voice(f"{AUTH_DIR}/sample_{i}.wav")

# Step 2: Record Unauthorized Voices
os.makedirs(UNAUTH_DIR, exist_ok=True)
for i in range(1, num_samples + 1):
    input(f"🛑 Ask someone else to speak for sample {i}. Press Enter to record...")
    record_voice(f"{UNAUTH_DIR}/sample_{i}.wav")

# Step 3: Extract Features (MFCC)
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc, axis=1)

X_train, y_train = [], []

# Load authorized samples
for file in os.listdir(AUTH_DIR):
    if file.endswith(".wav"):
        features = extract_features(os.path.join(AUTH_DIR, file))
        X_train.append(features)
        y_train.append(1)  # Label '1' for authorized user

# Load unauthorized samples
for file in os.listdir(UNAUTH_DIR):
    if file.endswith(".wav"):
        features = extract_features(os.path.join(UNAUTH_DIR, file))
        X_train.append(features)
        y_train.append(0)  # Label '0' for unauthorized user

X_train = np.array(X_train)

# Step 4: Train SVM Model
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
model = SVC(kernel="linear", probability=True)
model.fit(X_train, y_train)

# Step 5: Save Model & Scaler
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)
with open(SCALER_PATH, "wb") as f:
    pickle.dump(scaler, f)

print("✅ Model trained successfully with authorized & unauthorized voices!")