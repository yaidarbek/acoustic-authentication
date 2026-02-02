# Department of Computer Science

# BSCCS Final Year Project 2025- 2026

# Interim Report I

## 25CS

## Secure Offline P2P Acoustic Proximity Authentication between

## Smartphone and Laptop

## (Volume of )

## Student Name :^ AIDARBEK Yernur^

## Student No. : 57597935

## Programme Code : BSCCCU

## Supervisor : Prof HANCKE, Gerhard

## Petrus

## Date : October 22 , 2025

```
For Official Use Only
```

## Table of Contents


- 1 Introduction
   - 1.1 Motivation & Background Information
   - 1.2 Problem Statement:
   - 1.3 Proposed Solution:
   - 1.4 Project Aims
   - 1.5 Project Scope
- 2 Literature Review
   - 2.1 Radio Frequency (RF) Transmission:
      - 2.1.1 NFC
      - 2.1.2 Bluetooth
   - 2.2 Optical Transmission:
      - 2.2.1 QR code:
   - 2.3 Audio Transmission:
      - 2.3.1 Acoustic authentification:
- 3 Preliminary Design, Solution, System
   - 3.1 System Overview
   - 3.2 System Components
      - 3.2.1 Hardware Components
      - 3.2.2 Software Components
   - 3.3 Algorithm
      - 3.3.1 Challenge Generation:
      - 3.3.2 Acoustic Encoding and Transmission:
      - 3.3.3 Signal Reception and Decoding:
      - 3.3.4. Response Computation:
      - 3.3.5 Verification and Access Control:
   - 3.4 Testing and Experimental Design
      - 3.4.1 Testing Objectives
      - 3.4.2 Test Setup
      - 3.4.3 Testing Procedures
- 4 Preliminary Design, Solution, System
   - 4.1 Preliminary Testing Results
   - 4.2 Future Improvement
   - 4.3 Gantt Chart
- Monthly Logs
- 5 Reference list


## 1 Introduction

### 1.1 Motivation & Background Information

The widespread usage of electronic devices has become a definition of modern society. Securing
access to these devices is a fundamental challenge, as their compromise can lead to breaches of
personal privacy, financial loss, and critical infrastructure failure. The scale of this importance is
reflected in the investments in the cybersecurity market, which is projected to grow from USD
218.98 billion in 2025 to USD 562.77 billion by 2030 (Fortune Business Insights, 2025). In
response to this universal need for protection, a vast ecosystem of authentication methods has
been developed.
A significant limitation of many modern authentication systems is their dependence on an online
network connection for validation, such as contacting a central server for two-factor authentication
(2FA). As Gurevich et al. (2022) state, "the problem of secure communication and authentication
without online servers is fundamental" (p. 1). This paper, therefore, focuses specifically on
authentication methods that can be implemented securely in an offline environment, where devices
must establish trust without any network connectivity.

### 1.2 Problem Statement:

The main problem is that it is impossible to guarantee complete security with any authentication
method. Therefore, it is crucial to develop layered security mechanisms where the corruption of
one layer does not lead to the corruption of other layers (Grassi et al., 2020; Ometov et al., 2018).
For instance, current offline authentication technologies represent a fundamental trade-off
between security, accessibility, and implementation cost. NFC offers strong security but requires
specialized hardware not available across all devices. Bluetooth offers broader compatibility but
suffers from relay attacks due to its long range. QR codes ensure universal accessibility but lack
bidirectional communication for secure mutual authentication.


This creates gaps in the security system, particularly for RF-restricted and offline environments
where radio frequency methods may be compromised, jammed, or prohibited.

### 1.3 Proposed Solution:

This research proposes a new acoustic-based authentication system that addresses these gaps by
providing an additional security layer for , proximity-based authentication application, in RF-
restricted and offline environments.

### 1.4 Project Aims

This project aims to use standard audio hardware on laptops and phones as a transport layer for a
secure authentication protocol, replacing radio frequency or optical layers in scenarios where those
methods are inefficient. The main objective is to evaluate the feasibility of acoustic authentication
in terms of data transmission reliability and resistance to common attacks.

### 1.5 Project Scope

- A Python application for the laptop to manage challenges, responses, and access control.
- An iOS application to capture, decode, and respond to acoustic challenges.
- A functional demonstration where successful acoustic authentication unlocks a designated
    folder on the laptop.


## 2 Literature Review

Authentication technologies can be categorized by their transmission medium, each with distinct
trade-offs.

### 2.1 Radio Frequency (RF) Transmission:

#### 2.1.1 NFC

Near Field Communication (NFC) provides secure short-range communication (<10 cm) and
supports strong cryptography. According to Ravilia et al. (2024), NFC tokens use cryptographic-
response protocols, making the technology highly secure against threats like phishing and man-
in-the-middle (MITM) attacks. In addition, Ravilia et al. (2024) suggest that NFC is more
convenient than alternatives as it requires only a simple "tap" from the user.
While it can be used as a two-factor authenticator, which will be proximity-based and secure,
NFC-based two-factor authentication has its own issues. For instance, as Heartfield and Loukas
(2018) state, NFC is expensive and not common in the majority of laptops and desktop
technologies. Moreover, Francillon et al. (201 9 ) demonstrate the possibility of relay attacks
against short-range wireless protocols like NFC. They showed that the physical proximity
requirement is not a guarantee of presence, as the authentication session can be relayed over a
greater distance.
Although NFC is more secure against certain attacks like phishing and man-in-the-middle, and
can create a smoother authentication process than acoustic-based authentication, audio
components are more common. Therefore, the acoustic authentication method is more universally
accessible.

#### 2.1.2 Bluetooth

Bluetooth, which offers a greater range (up to 100 m), on the other hand, is more popular than
NFC technology. Padgette et al. (2017) state that the widespread adoption of Bluetooth makes this
technology a good base for the development of innovative cybersecurity applications. Bluetooth-


based solutions also offer a convenient way of authentication that is less cumbersome than
alternatives with secure authentication solutions (Mare et al., 2014). The Bluetooth protocol is
also evolving by adding more security measures. Modern BLE uses Secure Connections Pairing,
a strong method that provides protection against passive eavesdropping (Antonioli et al., 2020).
Despite the introduction of ECDH to the Bluetooth system does not help to safely solve relay
attacks. The most significant security flaw of Bluetooth for authentication is its relatively long
range(<100 m). This means that a device can be authenticated from different rooms within this
radius. Ryan (2013), an attacker can relay the Bluetooth signals between two devices that are far
apart, tricking them into believing they are in close proximity.
Acoustic authentication, despite not being a more popular technology than Bluetooth, solves its
core weakness, which is long proximity. Sound waves attenuates rapidly and allow for precise
time-of-flight measurements, acoustic systems can enforce close proximity**.** As noted by Huth et
al. ( 2015 ), this property of sound decreases the chances of relay attacks by ensuring the device is
close to the authenticator within centimeters, not meters, using physics.

### 2.2 Optical Transmission:

#### 2.2.1 QR code:

QR codes are a widely adopted optical method for user authentication. The main advantage is that
a QR code can contain a significant amount of data, making the authentication session efficient
and reliable without a round-trips (Eminagaoglu et al., 201 4 ). Tirfe et al. (20 21 ) state that it is also
resistant to man-in-the-middle (MITM) attacks.
On the other hand, one-way factor authentication can be considered a security flaw. Tirfe et al.
( 2021 ) suggest that this technology is vulnerable to remote session swapping attacks because it
does not have mutual authentication. It also depends on the phone's camera, which can be broken,
limiting secure authentication options.


Unlike the one-way visual channel of a QR code, an acoustic channel can easily be made
bidirectional. This helps to establish a secure communication session resistant to remote attackers
(Zhang et al., 2014 ).

### 2.3 Audio Transmission:

#### 2.3.1 Acoustic authentification:

This method uses sound waves to transmit data and has two major flaws. The acoustic channel
has a very low data rate compared to RF or optical links, making it unsuitable for large data
transfers and potentially resulting in higher latency during the authentication handshake (Mehrabi
et al., 20 20 ). In addition, performance can be degraded by noise, which leads to packet loss. This
necessitates robust error-correction and can reduce reliability in noisy real-world settings
(Nandakumar et al., 2014).
Even though the acoustic channel is not reliable in noisy environments, the characteristics of sound
waves can act as a preventive mechanism against relay attacks because sound waves attenuate
rapidly and are blocked by walls. This short physical range (<1m) enforces close proximity,
providing a natural defense against the long-distance relay attacks that are a critical flaw in
Bluetooth-based systems (Jakobsson & Wetzel, 2001). While the small data capacity poses
challenges, it is not problematic for this application since this project aims to transfer only the
cipher keys, which are small in size and do not require large data transfers. In addition, unlike
NFC or Bluetooth LE, it requires no specialized hardware, leveraging components present in
virtually all smartphones and laptops. This makes it a universally accessible solution that functions
completely offline (Schürmann & Sigg, 2011).
Therefore, despite the existence of NFC, Bluetooth, and QR code-based authentications that
provide a good level of security and are already in use by world-leading companies, they can still
have security or implementation flaws in the scenarios described above. Although the acoustic


channel does not solve all the issues of other authentication methods, it can cover security needs
in offline, RF-restricted environments that require close proximity between pairing devices.

## 3 Preliminary Design, Solution, System

### 3.1 System Overview

Acoustic authentication system will establish acoustic authentification channel between a
Phone(iPhone) and Laptop(MacBook). This channel relies on per to peer communication channel,
therefore it does not require connection to the Internet, or any type of 3 partyy technology. This
desgn helps to provide secure authentification Offline and RF-restricted environment.
The proposed authentification system operates through challenge-response authentication over an
acoustic channel. A laptop generates a cryptographic challenge, encodes it into an audible or near-
ultrasonic audio signal, and sends using speaker. The iPhone receives this signal, decodes it,
computes a cryptographic response using a shared secret, and transmits the response acoustically
back to the laptop. The laptop validates the response to complete or deny authentication.


### 3.2 System Components

The proposed acoustic authentication solution is designed using a collection of standard
hardware and custom software components. The system's building blocks can be logically
divided into two main categories: the physical hardware that handles acoustic transmission and
reception, and the software modules that manage the cryptographic and data-link protocols.

#### 3.2.1 Hardware Components

The system is designed to operate on commodity hardware, requiring no specialized equipment.
Its functionality relies on the standard audio input and output capabilities found on modern
laptops and smartphones, which together form the physical layer for data transmission.

- **Laptop Speakers:** The built-in or external audio output system of the laptop. Its primary
    function is to transmit the acoustic challenge by playing the encoded audio tones.
- **Laptop Microphone:** The standard integrated microphone on the laptop. It is
    responsible for recording the incoming acoustic response signal sent from the mobile
    device.
- **iPhone Speaker:** The standard loudspeaker on the iOS device. It is used to send back the
    encoded acoustic response tone sequence to the laptop.
- **iPhone Microphone:** The built-in microphone on the iOS device. Its role is to capture
    the initial acoustic challenge from the laptop and forward the signal to the software
    decoding module.

#### 3.2.2 Software Components

Complementing the hardware is a layered software stack that implements the core authentication
logic. These modules handle everything from low-level signal processing to high-level
cryptographic operations and user interaction, ensuring a robust and secure authentication
process.


- **Audio Interface Module** : Manages all audio input/output operations using PyAudio
    (Python) and AudioKit (Swift), handling recording, playback, and synchronization at a
    44.1 kHz sample rate.
- **Modulation & Demodulation Module:** Converts data between binary and acoustic
    signals using Frequency-Shift Keying (FSK) for transmission and employs FFT for
    frequency detection during reception.
- **Frame Construction Module:** Assembles data into structured frames with a Preamble,
    Header, Payload, and CRC checksum, managing the timing and structure of
    transmissions.
- **Challenge Generator:** Produces a cryptographically secure random nonce for each
    session using the secrets module (Python) or SecRandomCopyBytes (iOS).
- **Cryptographic Engine:** Computes and verifies HMAC-SHA256 hashes to ensure the
    integrity and authenticity of the challenge-response exchange.
- **Response Generator:** On the iOS device, computes the HMAC response to the received
    challenge and prepares it for acoustic transmission.
- **Verification and Access Control Module:** Compares the received response against the
    expected value and unlocks the secured resource upon a successful match.
- **Error Correction & Control Module:** Implements CRC-16 for error detection and
    manages retransmission protocols to ensure data reliability over the acoustic channel.
- **User Interface Layer (UI):** Provides the user-facing application on both devices, built
    with Swift UI for iOS and Tkinter/PyQt for the laptop

### 3.3 Algorithm

The core authentication mechanism employs a cryptographic challenge-response protocol that
uses acoustic channel. The protocol ensures mutual authentication through shared secret
verification while maintaining resistance to replay attacks


#### 3.3.1 Challenge Generation:

The initiator (laptop) generates a cryptographic challenge using the following procedure:
C = os.urandom(16) # 128-bit random challenge
R_expected = HMAC(K, C, digestmod='sha256')
_Algorithm Specification: The nonce C is generated using a cryptographically secure
pseudorandom number generator (CSPRNG) as specified by Barker and Kelsey (20 12 ). The
128 - bit length provides sufficient entropy (2^128 possible values) to prevent brute-force attacks.
The HMAC construction follows the standard by Krawczyk et al. (1997) using SHA-256 as the
underlying hash function, providing 128-bit security strength against collision attacks._

#### 3.3.2 Acoustic Encoding and Transmission:

The binary challenge C is converted to an acoustic signal using digital modulation techniques:
**Frequency-Shift Keying (FSK) Implementation:**

- Binary '0': Represented by frequency f₀ = 18000 Hz (near-ultrasonic)
- Binary '1': Represented by frequency f₁ = 19000 Hz
- Symbol duration: T_symbol = 50 ms
- Sampling rate: f_s = 44100 Hz
The modulated signal s(t) is constructed as:
s(t) = A · sin(2πf₀t) for binary '0'
s(t) = A · sin(2πf₁t) for binary '1'
_Technical Rationale: FSK modulation provides robustness against amplitude variations and
selective fading (Proakis & Salehi, 200 1 ). The near-ultrasonic frequency range (18-19 kHz)
minimizes audible disturbance while remaining within the frequency response of standard
laptop speakers and smartphone microphones, typically capable of 16-22 kHz response
(Michalevsky et al., 2014)._


#### 3.3.3 Signal Reception and Decoding:

The receiver (iOS device) processes the incoming acoustic signal through a demodulation
pipeline:
**Preprocessing Stages:**

1. _Band-pass filtering_ : 17-21 kHz Butterworth filter to remove out-of-band noise
2. _Normalization_ : Automatic gain control to compensate for distance-dependent attenuation
3. _Frame synchronization_ : Preamble detection using Barker code sequence
4. _FSK demodulation: Goertzel algorithm (Sysel & Rajmic, 2012) for efficient frequency_
    _detection_
The Goertzel algorithm computes the energy at frequencies f₀ and f₁:
P₀ = |X(f₀)|², P₁ = |X(f₁)|²
Decision: binary '0' if P₀ > P₁, else binary '1'

#### 3.3.4. Response Computation:

Upon successful decoding of challenge C, the prover computes:
text
R_device = HMAC(K, C)
using the same HMAC-SHA256 parameters as the authenticator. The shared secret K is securely
stored in the device's keychain, protected by the iOS Secure Enclave.

#### 3.3.5 Verification and Access Control:

The authenticator performs a constant-time comparison:
if secure_compare(R_device, R_expected):
grant_access()
else:
deny_access()


The secure_compare() function implements constant-time comparison to prevent timing attacks
(Brumley & Boneh, 200 5 ), ensuring the comparison time is independent of the number of
matching bytes **Protocol Security Properties:**

- _Replay Protection_ : Each challenge is used only once (nonce)
- _Forward Secrecy_ : Compromise of K doesn't reveal past session keys
- _Mutual Authentication_ : Both parties prove knowledge of K
- _Proximity Assurance_ : Acoustic channel limits effective range to ~1 meter

### 3.4 Testing and Experimental Design

#### 3.4.1 Testing Objectives

The testing phase aims to evaluate:

- **Functional accuracy** – correctness of authentication responses.
- **Signal reliability** – success rate of acoustic data transmission under varying noise
    conditions.
- **Security robustness** – resistance to replay, relay, and eavesdropping attacks.
- **Practical usability** – response time, error rate, and real-world feasibility.

#### 3.4.2 Test Setup

```
Parameter Configuration
```
```
Test Environment Quiet indoor room (baseline), moderate noise (office), high noise
(café)
Devices Laptop (MacBook/Windows PC) & iPhone
Sampling Rate 44.1 kHz
Encoding Scheme FSK (two-tone), adjustable frequency separation
Number of Trials 50 per environment
```

```
Parameter Configuration
Distance Between
Devices
10 cm – 100 cm
```
#### 3.4.3 Testing Procedures

1. **Functional Validation** :
    o Run the full authentication sequence multiple times under ideal conditions.
    o Measure success rate and transmission latency.
2. **Noise Tolerance Tests** :
    o Introduce controlled background noise levels (e.g., white noise at 40–70 dB).
    o Measure decoding success rate and error rate.
3. **Security Tests** :
    o Attempt replay attacks by recording and re-transmitting previous response
       signals.
    o Attempt distance-based relay attacks (>1m) to confirm proximity enforcement.
4. **Performance Metrics** :
    o **Success Rate (%) = Successful Authentications ÷ Total Attempts**
    o **Average Latency (ms)** between challenge emission and authentication
       completion.
    o **Bit Error Rate (BER)** to assess transmission reliability.


## 4 Preliminary Design, Solution, System

### 4.1 Preliminary Testing Results

The initial two-month development phase has successfully resulted in a minimal viable
prototype (MVP) that validates the core technical premise. Proof of concept demonstrated a
complete, end-to-end authentication cycle under silent conditions. The system reliably transmits
a cryptographic nonce from a laptop to an iOS device and subsequently receives and
successfully verifies the correct HMAC-SHA256 response. This successful proof-of-concept,
which culminates in a software-based "access granted" signal on the laptop, provides a stable
and verified foundation for all subsequent development.

### 4.2 Future Improvement

Building upon the functional MVP, the next phase of development will focus on enhancing the
system's robustness, security, and practical usability. Key areas for improvement include:

- **Implementing a Robust Data-Link Layer:** The current simple transmission will be
    replaced with a structured frame protocol featuring preambles for synchronization,
    payload length headers, and CRC checksums for error detection to significantly improve
    reliability.
- **Introducing Error Correction:** We will integrate forward error correction codes, such
    as Reed-Solomon, to correct bit errors without requiring retransmission, thereby
    increasing success rates in less-than-ideal acoustic environments.
- **Hardening Security:** The system will be fortified against replay attacks by
    implementing a secure nonce management system that logs used challenges.
    Furthermore, all comparison operations (e.g., HMAC verification) will be made
    constant-time to prevent timing-based side-channel attacks.


- **Developing a Basic User Interface:** A simple graphical user interface (GUI) will be
    developed for both the laptop and iOS application to replace command-line operations,
    providing users with clear status feedback and control over the authentication process.

### 4.3 Gantt Chart

## Monthly Logs


## 5 Reference list

Antonioli, D., Tippenhauer, N. O., & Rasmussen, K. (2020). Key negotiation downfalls of the
Bluetooth standard. _ACM Transactions on Privacy and Security_ , *23*(3), 1–

28. https://doi.org/10.1145/
Barker, E., & Kelsey, J. (201 2 ). *NIST Special Publication 800-90A: Recommendation for
random number generation using deterministic random bit generators*. National Institute
of Standards and Technology. doi/abs/10.5555/
Brumley, D., & Boneh, D. (2005). Remote timing attacks are practical. _Computer
Networks_ , _48_ (5), 701-716. https://doi.org/10.1016/j.comnet.2005.01.
Eminagaoglu, M., Cini, E., Sert, G., & Zor, D. (2014, September). A two-factor authentication
system with QR codes for web and mobile applications. In _2014 Fifth International
Conference on Emerging Security Technologies_ (pp. 105-112). IEEE.
DOI **:** 10.1109/EST.2014.
Francillon, A., Danev, B., & Capkun, S. (2019). Relay attacks on passive keyless entry and start
systems in modern cars. _IEEE Transactions on Dependable and Secure
Computing_ , *16*(1) https://www.researchgate.net/publication/220333841_Relay_Attack
s_on_Passive_Keyless_Entry_and_Start_Systems_in_Modern_Cars
Fortune Business Insights. (2025, September 25). *Cybersecurity market size, share & industry
analysis, 2025-2032* (Report ID: 101165). https://www.fortunebusinessinsights.com/
Grassi, P. A., Fenton, J. L., Newton, E. M., Perlner, R. A., Regenscheid, A. R., Burr, W. E., Richer,
J. P., Lefkovitz, N. B., Danker, J. M., Choong, Y.-Y., Greene, K. K., & Theofanos, M. F.
(2020). _Digital identity guidelines: Authentication and lifecycle management_ (NIST
Special Publication 800-63B). National Institute of Standards and
Technology. https://doi.org/10.6028/NIST.SP.800-63b


Heartfield, R., & Loukas, G. (2018). A taxonomy of attacks and a survey of defence mechanisms
for semantic social engineering attacks. _ACM Computing Surveys_ , *50*(3), 1–

39. https://doi.org/10.1145/
Huth, Christopher & Zibuschka, Jan & Duplys, Paul & Güneysu, Tim. (2015). Securing systems
on the Internet of Things via physical properties of devices and communications. 9th
Annual IEEE International Systems Conference, SysCon 2015 - Proceedings. 8- 13.
DOI:10.1109/SYSCON.2015.
Jakobsson, M., & Wetzel, S. (2001, April). Security weaknesses in Bluetooth. In _Cryptographers’
Track at the RSA Conference_ (pp. 176-191). Berlin, Heidelberg: Springer Berlin
Heidelberg. https://link.springer.com/chapter/10.1007/3- 540 - 45353 - 9_
Krawczyk, H., Bellare, M., & Canetti, R. (1997). RFC2104: HMAC: Keyed-hashing for message
authentication. https://doi.org/10.17487/RFC
Mare, S., Markham, A., Cornelius, C., Peterson, R., & Kotz, D. (2014). ZEBRA: Zero-effort
bilateral recurring authentication. _2014 IEEE Symposium on Security and Privacy_ , 705–
720. https://doi.org/10.1109/SP.2014.
Mehrabi, A., Mazzoni, A., Jones, D., & Steed, A. (2020). Evaluating the user experience of
acoustic data transmission: A study of sharing data between mobile devices using
sound. _Personal and Ubiquitous Computing_ , _24_ (5), 655-668.
Michalevsky, Y., Boneh, D., & Nakibly, G. (2014). Gyrophone: Recognizing speech from
gyroscope signals. In _23rd USENIX Security Symposium (USENIX Security 14)_ (pp. 1053-
1067).https://www.usenix.org/conference/usenixsecurity14/technical-
sessions/presentation/michalevsky
Nandakumar, R., Chintalapudi, K. K., & Venkatesan, R. (2014). Dhwani: Secure peer-to-peer
acoustic NFC. _ACM SIGCOMM Computer Communication Review_ , *44*(4), 63–
74. https://conferences.sigcomm.org/sigcomm/2013/papers/sigcomm/p63.pdf


Ometov, A., Bezzateev, S., Mäkitalo, N., Andreev, S., Mikkonen, T., & Koucheryavy, Y. (2018).
Multi-factor authentication: A survey. _Cryptography_ , *2*(1),

1. https://doi.org/10.3390/cryptography
Padgette, J., Bahr, J., Batra, M., Holtmann, M., Smithbey, R., Chen, L., & Scarfone, K.
(2017). _Guide to Bluetooth security_ (NIST Special Publication 800-121 Rev. 2). National
Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-121r
Proakis, J. G., & Salehi, M. (2001). _Digital communications_ (Vol. 4, pp. 593-620). New York:
McGraw-hill.
Ryan, M. (2013). _Bluetooth: With low energy comes low security_. 7th USENIX Workshop on
Offensive Technologies (WOOT
13). https://www.usenix.org/conference/presentation/ryan
Ravilla, Harshavardhan & Kulkarni, Pooja & Sayal, Rishi. (2024). Study and Analysis of FIDO
Passwordless Web Authentication. DOI:10.1007/978- 981 - 97 - 4727 - 6_
Tirfe, Dereje, and Vivek Kumar Anand. "A survey on trends of two-factor
authentication." _Contemporary Issues in Communication, Cloud and Big Data Analytics:
Proceedings of CCB 2020_. Singapore: Springer Singapore, 2021. 285- 29
https://link.springer.com/chapter/10.1007/978- 981 - 16 - 4244 - 9_
Schürmann, D., & Sigg, S. (2011). Secure communication based on ambient audio. _IEEE
Transactions on mobile computing_ , _12_ (2), 358-370. DOI **:** 10.1109/TMC.2011.
Sysel, P., & Rajmic, P. (2012). Goertzel algorithm generalized to non-integer multiples of
fundamental frequency. _EURASIP Journal on Advances in Signal Processing_ , _2012_ (1),
56. https://link.springer.com/article/10.1186/1687- 6180 - 2012 - 56
Zhang, B., Zhan, Q., Chen, S., Li, M., Ren, K., Wang, C., & Ma, D. (2014). Enabling Keyless
Secure Acoustic Communication for Smartphones. _IEEE internet of things journal_ , _1_ (1),
33 - 45. DOI **:** 10.1109/JIOT.2014.



