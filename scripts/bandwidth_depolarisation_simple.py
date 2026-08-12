import numpy as np
import matplotlib.pyplot as plt


C = 299792458.0  # speed of light, m/s


def bandwidth_depolarisation(rm,freq_min,freq_max,nchan,npoints=2000):
    """
    Calculate bandwidth depolarisation caused by Faraday rotation.

    Parameters
    ----------
    rm : float
        Rotation measure in rad/m^2.

    freq_min : float
        Minimum observing frequency in Hz.

    freq_max : float
        Maximum observing frequency in Hz.

    nchan : int
        Number of frequency channels.

    npoints : int
        Number of points used to sample the band.

    Returns
    -------
    freq : ndarray
        Frequency array in Hz.

    dchi : ndarray
        Polarization-angle rotation across each channel in radians.

    fraction_remaining : ndarray
        Fraction of linear polarization remaining.

    fraction_lost : ndarray
        Fraction of linear polarization lost.
    """

    channel_width = (freq_max - freq_min) / nchan

    freq = np.linspace(freq_min, freq_max, npoints)

    nu_low = freq - channel_width / 2
    nu_high = freq + channel_width / 2

    lambda2_low = (C / nu_low)**2
    lambda2_high = (C / nu_high)**2

    delta_lambda2 = np.abs(lambda2_low - lambda2_high)

    # Change in polarization angle across one channel
    dchi = np.abs(rm) * delta_lambda2

    # Finite-channel bandwidth depolarisation
    fraction_remaining = np.abs(np.sinc(dchi / np.pi))
    fraction_lost = 1 - fraction_remaining

    return (freq,dchi,fraction_remaining,fraction_lost,channel_width)


# ==================================================
# User parameters
# ==================================================

RM = 33000.0

FREQ_MIN = 2.185e9
FREQ_MAX = 3.0625e9

NCHAN = 1024


# ==================================================
# Calculation
# ==================================================

freq, dchi, remaining, lost, channel_width = (bandwidth_depolarisation(rm=RM,freq_min=FREQ_MIN,freq_max=FREQ_MAX,nchan=NCHAN))


# ==================================================
# Summary
# ==================================================

print("=" * 60)
print("Bandwidth depolarisation calculation")
print("=" * 60)

print(f"RM                : {RM:.0f} rad/m^2")
print(f"Frequency range   : {FREQ_MIN/1e9:.4f} - {FREQ_MAX/1e9:.4f} GHz")
print(f"Number of channels: {NCHAN}")
print(f"Channel width     : {channel_width/1e3:.2f} kHz")

print("\nLowest frequency")
print("----------------")
print(f"Frequency         : {freq[0]/1e9:.4f} GHz")
print(f"Δχ per channel    : {np.degrees(dchi[0]):.3f} deg")
print(f"Pol. remaining    : {remaining[0]*100:.3f}%")
print(f"Pol. lost         : {lost[0]*100:.3f}%")

print("\nHighest frequency")
print("-----------------")
print(f"Frequency         : {freq[-1]/1e9:.4f} GHz")
print(f"Δχ per channel    : {np.degrees(dchi[-1]):.3f} deg")
print(f"Pol. remaining    : {remaining[-1]*100:.3f}%")
print(f"Pol. lost         : {lost[-1]*100:.3f}%")

print("\nMaximum bandwidth depolarisation")
print("--------------------------------")
imax = np.argmax(lost)

print(f"Frequency         : {freq[imax]/1e9:.4f} GHz")
print(f"Maximum loss      : {lost[imax]*100:.3f}%")


# ==================================================
# Plot
# ==================================================

plt.figure(figsize=(8, 5))

plt.plot(freq / 1e9,lost * 100)

plt.xlabel("Frequency (GHz)")
plt.ylabel("Bandwidth depolarisation (%)")
plt.tight_layout()
plt.show()
