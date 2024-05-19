# MyStranger.in

Welcome to the GitHub repository of **MyStranger.in**, a social networking site that connects college students within a 60 km radius of their college. This platform is built using Django Channels and other technologies, providing an exclusive community for college students.

## About MyStranger.in

MyStranger.in is designed to cater to the specific needs of college students by providing them with an exclusive nearby college community. The platform stands by the idea that every college student deserves a platform that caters to their specific needs.

### Features

- **Random Connection**: Users can randomly connect with other nearby college students using the text/video feature.
- **Posts**: Users can see & create posts within their exclusive nearby college's community.
- **Blind Dates**: Users can go on blind dates with other nearby college students. Only females can set the location & time of the date.

We ensure that only college students can join the site by using the .edu-verification system.

## Technical Details

### Tech Stack

- HTML
- CSS
- JavaScript
- Django with Channels
- PostgreSQL
- Redis
- WebRTC
- Mapbox API
- Google Cloud

### Key Implementations

- **Peer-to-Peer Connection**: Leveraged WebRTC technology and STUN servers to facilitate an Omegle-like video chat feature, enabling real-time, anonymous interactions among users.
- **Real-Time Messaging**: Utilized Django Channels to construct a dynamic messaging section, similar to Facebook’s messaging system, allowing instantaneous text communication.
- **Multi-Layered Comment Section**: Implemented a multi-layered comment section using the Modified Preorder Tree Traversal (MPTT) data structure in Django, enhancing user engagement and interaction.
- **Location-Based Search**: Integrated the Mapbox API to enable a map search functionality, allowing users to fetch their university and connect with students based on university locations.

We hope you find this repository useful for understanding the workings of MyStranger.in. Feel free to explore the code and contribute!
