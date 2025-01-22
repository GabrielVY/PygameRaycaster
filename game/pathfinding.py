from game.world import World

# This uses A* Algorithm
# Thanks: https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2

class PathFinder:

    class Node:
        def __init__(self, f, g, h, x, y, parent=None) -> None:
            self.parent = parent

            self.f = f # Total cost of this node
            self.g = g # Distance between current node and start node
            self.h = h # Estimated heuristic/distance between current node and end node

            # Position on the map
            self.x = x
            self.y = y

            # Last path found
            self.path_found = []

        def __eq__(self, other):
            return (self.x == other.x and self.y == other.y)

        def __repr__(self) -> str:
            return f'Node[f={self.f}, g={self.g}, h={self.h}, x={self.x}, y={self.y}]'

    def __init__(self, linked_entity=None) -> None:
        self.gamemap = World.gamemap
        self.linked_entity = linked_entity # If there's a link, it will always start searching from the entity map position

    def search_path(self, end_pos, start_pos=None, allow_diagonals=False):
        x2, y2 = end_pos
        x2, y2 = int(x2), int(y2)

        if start_pos is None:
            x1, y1 = self.linked_entity.get_map_pos()
            x1, y1 = int(x1), int(y1)
        else:
            x1, y1 = int(start_pos[0]), int(start_pos[1])

        # All possible direction of movements
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        if not allow_diagonals:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        # Gamemap of wall
        mapW = self.gamemap.mapW
        map_width, map_height = self.gamemap.width, self.gamemap.height
        
        # Final node (Just used for the final comparison of position)
        end_node = PathFinder.Node(0, 0, 0, x2, y2)

        # First node has no cost (except for h)
        open_nodes = [PathFinder.Node(0, 0, 0, x1, y1)]
        closed_nodes = []

        # Limits the search depth
        MAX_DEPTH = 5000
        current_search_index = -1

        current_node = None # The current node will also be the final node
        while len(open_nodes) > 0:
            current_search_index += 1
            if current_search_index >= MAX_DEPTH:
                print("WARNING: Reached Maximum Pathfinding Depth")
                return []

            # Get the current node (Node with the lowest F cost)
            current_node = open_nodes[0]
            current_index = 0
            for index, node in enumerate(open_nodes):
                if node.f < current_node.f:
                    current_node = node
                    current_index = index

            # Get node with the lowest cost and put it in the closed list
            open_nodes.pop(current_index)
            closed_nodes.append(current_node)

            # This is the end goal

            if current_node == end_node:
                end_node = current_node
                break

            # Get node children (x, and y map positions)
            children = []

            # Calculate the paths for each of the 8 squares around the current node
            for x, y in directions:
                # Convert it to node position
                x = current_node.x + x
                y = current_node.y + y

                # Valid position?
                if not (x >= 0 and x < map_width and y >= 0 and y < map_height):
                    continue

                # Hit a wall
                if mapW[y][x] > 0:
                    continue

                children.append(PathFinder.Node(-1, -1, -1, x, y, parent=current_node))

            for child in children:
                # Child is already in the closed list
                collided = False
                for closed_node in closed_nodes:
                    if child == closed_node:
                        collided = True

                if collided:
                    continue
                
                # Add it to the open list
                cx, cy = child.x, child.y
                child.g = current_node.g + 1
                child.h = ((cx - x2)**2) + ((cy - y2)**2)
                child.f = child.g + child.h

                # Child is already in the open list
                collided = False
                for open_node in open_nodes:
                    if open_node == child and child.g > open_node.g:
                        collided = True

                if collided:
                    continue

                # If there was no collision just add it to the open node list  
                open_nodes.append(child)

        # Now get the path (Working backwards using the node parents)
        path = []
        current_node = end_node
        while current_node is not None:
            path.append((current_node.x, current_node.y))
            current_node = current_node.parent

        # Reverse the path, saves to itself and return it
        self.path_found = path[::-1]

        # Return reversed path
        return self.path_found