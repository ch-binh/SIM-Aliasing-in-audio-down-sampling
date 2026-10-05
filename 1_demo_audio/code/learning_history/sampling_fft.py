import numpy as np
import matplotlib.pyplot as plt

# Sampling
fs = 60  # Hz
T = 1  # second
t = np.arange(0, T, 1 / fs)

# Signal: 50 Hz + 120 Hz
x = np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)

# FFT
X = np.fft.fft(x)

freq = np.fft.fftfreq(len(x), d=1 / fs)

# Only positive frequencies
half = len(freq) // 2

# Create one figure with two plots
fig, ax = plt.subplots(1, 2, figsize=(12, 4))

# -------------------------
# Time domain
# -------------------------
ax[0].plot(t, x)

ax[0].set_title("Time Domain")
ax[0].set_xlabel("Time (s)")
ax[0].set_ylabel("Amplitude")
ax[0].grid()

# -------------------------
# Frequency domain
# -------------------------
ax[1].plot(freq[:half], np.abs(X[:half]))

ax[1].set_title("Frequency Domain")
ax[1].set_xlabel("Frequency (Hz)")
ax[1].set_ylabel("Magnitude")
ax[1].grid()

plt.tight_layout()
plt.show()
