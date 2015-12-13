# Activity-Based Indoor Localization

Project Abstract
------
Global positioning system is inaccurate for indoor localization, and the growing need for a reliable indoor positioning system (IPS) has yet to be filled. We propose a new technique for indoor localization using activity recognition from motion data. Using only a standard smartphone app, we collect the user’s motion data from the phone’s onboard accelerometer, gyroscope, and compass. This data is then sent to a server for processing and classification. The classifier decides which activity the person is engaged in (e.g. walking, sitting, etc.) and this information is used as a sensation for a particle filter based localization system. Combined with a simple odometry and turning detector, we are able to correctly localize users inside a university building. This can be useful for many applications, but we are specifically interested in exploring its effectiveness in an office setting andworking towards an intelligent building.

A demo of this work in simulation can be found here: https://youtu.be/gFB34H4qNEM.
