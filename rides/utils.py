from network.models import Node, Edge
from .models import CarpoolRequest

def create_path(start_node, end_node):
    if start_node == end_node:
        return [start_node]
        
    queue = [start_node] 
    visited = {start_node}
    parent = {}
    found = False
    while queue:
        popped = queue.pop(0)
        if popped == end_node:
            found = True
            break
        for edge in popped.outgoing.all():
            neighbor = edge.next_node
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                parent[neighbor] = popped

    if not found:
        return []
    
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

def get_passengers_at_hop(trip, hop_index):
    confirmed_offers = trip.offers.filter(status='A')
    count = 0
    for offer in confirmed_offers:
        if offer.pickup_order <= hop_index <= offer.dropoff_order:
            count += 1
    return count

def calculate_fare(trip, pickup_node, dropoff_node, p=10, base_fee=5):
    remaining = list(trip.route.filter(passed=False).order_by('order'))
    remaining_nodes = [n.node for n in remaining]
    original_length = len(remaining_nodes) - 1
    
    current = remaining_nodes[0]
    destination = remaining_nodes[-1]
    
    new_length = (
        len(create_path(current, pickup_node)) - 1 +
        len(create_path(pickup_node, dropoff_node)) - 1 +
        len(create_path(dropoff_node, destination)) - 1
    )
    
    detour = new_length - original_length
    
    pickup_path = create_path(current, pickup_node)
    pickup_order = len(pickup_path) - 1
    dropoff_order = pickup_order + len(create_path(pickup_node, dropoff_node)) - 1
    num_hops_of_passenger = dropoff_order - pickup_order
    
    fare = base_fee
    for i in range(num_hops_of_passenger):
        fare += p * (1 / (get_passengers_at_hop(trip, pickup_order + i) + 1))
    
    return detour, round(fare, 2), pickup_order, dropoff_order