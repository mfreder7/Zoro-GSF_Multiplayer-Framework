# Zoro-GSF_Multiplayer-Framework - Game server system & Framework

![Coverage](coverage.svg)

The goal is to build a robust and efficient solution designed to minimize latency and overhead through a stack of custom protocols in a lean server environment. This project provides a foundational game server structure optimized for self-hosting, ensuring smooth and responsive multiplayer experiences. The intention is to provide a "front-end" centric multiplayer framework that enables developers to a worry free experience in regards to the intricacies of networking.

## Features (working)

- **FastAPI API**: A scalable and high-performance API built with FastAPI, handling routes for lobbies and player management.
- **Custom UDPs**: Built with a "game development" forward mindset for best throughput and control as needed.
  - Reliable and Unreliable UDP sockets are functioning and accept connections when created.
  - Built in UDP manager is operational it includes features such as: socket resource cleanup (after a certain time-period with 0 clients being connected), port scanning, connect/disconnect handlers (safe exit), and connected client tracking.
- **OAS 3.1**: Thanks to FastAPI `/docs` gets generated for API endpoints, so feel free to spin it up and poke around.

## WIP (not working.. yet)

- x Tests are continuous WIP, so they may be broken while I do rapid releases early on. Depends on how excited or tired I am when a feature gets completed.
- x Features (more to come), keep an eye on the issues tab. **I will be treating the issues panel as a roadmap and open invite to the community.**
- x Front-end for the API.
- x Packet handling
- x Declared game logic parsing

### Running API Locally

To execute the API locally, ensure you have the necessary dependencies installed `pip install requirements.txt ` and run:

```sh
uvicorn app.main:app --reload --host <ip-address> --port <port>
```

### Running Tests Locally

To execute the unit tests locally, ensure you have the necessary dependencies installed and run:

```sh
pytest
```

If you want to test the UDP sockets, I temporarily created a python file you can run with:

```sh
 python -m app.tests.runnable.run_to_test_udp <client_name> "http://localhost:<port>"
```

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements or bug fixes.

### License

Apache-2.0 license

### Like this?

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L01PGZ3)
