from network.models import Node, Edge

def create_path(start_node, end_node):
    queue = [start_node]
    visited = [start_node]
    parent = {}
    while queue:
        popped = queue.pop(0)
        if popped == end_node:
            break
        for edge in popped.start_from.all():
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