from routers.peer_router import peer_router
from routers.tracker_router import tracker_router

def get_all_routes():
    routes = [tracker_router, peer_router]
    return routes 


