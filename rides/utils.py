from network.models import Node, Edge

def create_path(start_node, end_node):
    queue = [start_node] 
    visited = [start_node]
    parent = {}
    while queue:
        popped = queue.pop(0)
        if popped == end_node:
            break
        for edge in popped.outgoing.all():
            neighbor = edge.next_node
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)
                parent[neighbor] = popped
    
    route = [end_node]
    j = parent[end_node]
    while j != start_node:
        route.append(j)
        j = parent[j]
    route.append(start_node)
    return route[::-1]

def nodes_within_2(node):
    result = set() # to avoid duplicates
    for edge in node.outgoing.all():
        result.add(edge.next_node)
        for edge2 in edge.next_node.outgoing.all():
            result.add(edge2.next_node)
    return result

def is_request_visible(trip, carpool_request):
    remaining = trip.route.filter(passed=False).order_by('order')
    nearby_nodes = set()
    for route_node in remaining:
        nearby_nodes.update(nodes_within_2(route_node.node))
        nearby_nodes.add(route_node.node)  # include the route nodes themselves
    
    return (carpool_request.pickup_node in nearby_nodes and 
            carpool_request.dropoff_node in nearby_nodes)

def get_visible_requests(trip):
    pending_requests = CarpoolRequest.objects.filter(status='P')
    return [req for req in pending_requests if is_request_visible(trip, req)]