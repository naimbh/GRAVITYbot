# Plain-language glossary for Gravity Spy volunteers

Use an entry only when the term appears in this week's important events. Keep each explanation to one sentence.

## Detector state
- **Observing / Observation mode:** the detector is in its best, stable state and its data are used for science. Glitches that matter to Gravity Spy come from this time.
- **NLN (Nominal Low Noise):** the fully locked, lowest-noise state the detector reaches just before it goes to Observing.
- **Lock / locked:** the laser light is held resonant in the detector's arms, so it can measure tiny motions. The detector must be locked to take useful data.
- **Lockloss:** the detector suddenly loses lock and stops taking useful data until it relocks. The moments just before a lockloss often contain large glitches.
- **Relocking / lock acquisition:** the automated sequence that brings the detector back to a locked state after a lockloss. It can take from minutes to hours.
- **Duty cycle:** the share of time the detector was Observing.
- **Range (Mpc):** how far away the detector could detect a pair of merging neutron stars. A sudden range drop means extra noise.
- **Maintenance (Tuesday):** a weekly planned period when the detector is taken out of Observing for repairs and work.
- **Commissioning:** planned time when scientists tune or test the detector instead of Observing.
- **Vent:** the vacuum system is opened to air for hardware work. No Observing data exist during a vent.

## Parts of the detector
- **DARM:** the main measurement channel, the difference in length of the two arms. This is the signal Gravity Spy glitches appear in.
- **ETMX / ETMY (End Test Mass):** the large mirrors at the far ends of the X and Y arms. "ETMX glitches" are brief disturbances linked to the X-end mirror, and they have caused locklosses.
- **ITM (Input Test Mass):** the large mirrors at the near ends of the arms.
- **ESD (Electrostatic Drive):** applies electric forces to push a test mass. Problems with it can add noise or glitches.
- **Suspension (SUS):** the pendulums that hang the mirrors, isolating them from ground motion.
- **ISI and HEPI:** the active platforms that cancel ground shaking before it reaches the mirrors.
- **Squeezer (SQZ):** a system that injects a special state of light to reduce quantum noise. Changes to it can change the noise level, especially at high frequencies.
- **OPO, PMC, filter cavity (FC):** parts of the squeezer. When one loses lock, the detector can briefly drop out of Observing.
- **NLG (nonlinear gain):** a setting that controls how strongly the squeezer works.
- **OMC (Output Mode Cleaner):** a filter that cleans the light just before it is measured.
- **TCS (Thermal Compensation System), CO2 laser, ring heater:** heat the mirrors to correct their shape. Changes affect how well the detector stays aligned and locked.
- **ASC / LSC:** the automatic control loops that keep the mirrors aligned (ASC) and at the right lengths (LSC). Noise in them can leak into DARM.
- **A2L (angle-to-length):** how much a mirror tilting turns into a false length signal. Tuning it reduces low-frequency noise.
- **Calibration lines:** small, deliberate signals at fixed frequencies that run all the time to track the detector's calibration. They show up as steady narrow lines in the data, not glitches.
- **Calibration sweep / measurement (broadband, simulines):** a scheduled measurement, usually weekly, in which test signals are swept across many frequencies. The detector is taken out of Observing while it runs, so its data are not used by Gravity Spy; it is different from the always-on calibration lines.
- **Guardian:** the software that automatically runs the detector's states (locking, Observing, and so on).
- **BRS (Beam Rotation Sensor):** a sensor at the end stations that measures how much the ground tilts, so the seismic isolation can ignore tilt during wind.
- **PEM (Physical Environment Monitoring):** sensors (seismometers, microphones, magnetometers, weather) that record the environment.

## Noise and glitches
- **Glitch:** a short burst of noise in the data that is not a gravitational wave. Gravity Spy volunteers classify these.
- **Line:** noise at one steady frequency. A **comb** is a set of evenly spaced lines.
- **Scattered light:** stray laser light that bounces off moving surfaces and back into the beam, often producing arch-shaped glitches at low frequency.
- **Violin modes:** the fibers holding the mirrors vibrate like violin strings, near 500 Hz and its multiples. They are "rung up" (excited) after a lockloss and have to be damped.
- **Microseism:** constant low-frequency ground shaking caused by ocean waves. High microseism makes locking harder and can increase scattered light.
- **Earthquake mode:** a setting that hardens the seismic isolation when an earthquake's waves arrive.
- **Injection / excitation:** a deliberate test signal put into the detector. Data with injections can show features that are not natural glitches.
- **Hardware injection:** a fake gravitational-wave signal added on purpose to test the analysis.
- **DetChar / DQ shift:** the team that studies data quality. Its weekly reports list glitch rates, noisy periods and their suspected causes.
