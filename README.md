# Activity-Based Indoor Localization

Project Abstract
------
Global positioning system is inaccurate for indoor localization, and the growing need for a reliable indoor positioning system (IPS) has yet to be filled. We propose a new technique for indoor localization using activity recognition from motion data. Using only a standard smartphone app, we collect the user's motion data from the phone’s onboard accelerometer, gyroscope, and compass. This data is then sent to a server for processing and classification. The classifier decides which activity the person is engaged in (e.g. walking, sitting, etc.) and this information is used as a sensation for a particle filter based localization system. Combined with a simple odometry and turning detector, we are able to correctly localize users inside a university building. This can be useful for many applications, but we are specifically interested in exploring its effectiveness in an office setting andworking towards an intelligent building.

See report.pdf for the full project report.


BWI Sensors App
------
Our iOS app collects data from the device's accelerometer, gyroscope, and compass while the phone is in the user's pocket. It is stored locally on the iPhone, and is then exported via email for classification. It is also possible to stream this data in real time over a TCP connection, but our app does not currently support this.


Activity Classification
------
(Source code not available).

This part of the project is a neural network classifier that takes the motion data from the phone and determines what the user is doing. For example, they may be walking, standing, going up or down the stairs, etc. This stage of the process should also determine odometry (how fast the user is moving) and whether the user is turning. This information is then sent to the particle filter.


Particle Filter
------
This is the final step of our pipeline. The particle filter receives classifier output and weighs regions of the building map accordingly. As an example, if the user is walking, the weights of all hallways will be high. The particles are also updated by being moved forward and turned based on the odometry and turning rate of the user.

Our particle filter also supports a simulation mode, where the user's position can be simulated and recorded directly on the map. This allows us to test the particle filter's performance without requiring real data to be used.

A demo of this simulation and the particle filter can be found here: https://youtu.be/gFB34H4qNEM.
