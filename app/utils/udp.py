# TODO: Build out our UDP class to handle sending and receiving UDP packets

# The thought is to reduce the latency by separating the game communication into two different classes: 
# one for UDP and one for Server-Sent Events (SSE). 

# The UDP class will handle:
# As close to real-time bidirectional communication as possible. This will allow us to send updates to the client
# and receive updates from the client in real-time, which will reduce the latency and improve the overall performance of
# the game.

# This will be useful for recieving and sending unreliable updates, such as player movement, player actions, and other
