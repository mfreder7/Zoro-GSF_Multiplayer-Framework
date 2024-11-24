# TODO: Build out our SSE class to handle Server-Sent Events (SSE)

# The thought is to reduce the latency by separating the game communication into two different classes: 
# one for UDP and one for Server-Sent Events (SSE). 

# The SSE class will handle:
# One-way communication from the server to the client. We will use this to communicate reliable updates to the client,
# For instance, when a player joins a lobby or when a player leaves a lobby. We will also use this for things like score updates and game state updates that can be reliable.