import gc
import sys
from UATMapper import UATMapper

def calculate_distances(predicted_ids, original_ids):
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()
    
    distances = {}

    for predicted_id in predicted_ids:
        for original_id in original_ids:
            # Find the shortest path between predicted and original
            shortest_path = thesaurus.find_shortest_path(predicted_id, original_id)

            if shortest_path:
                distances[(predicted_id, original_id)] = (len(shortest_path) - 1, shortest_path)
            else:
                # If no path is found, return None for that pair
                distances[(predicted_id, original_id)] = (None, "No path found")
    
    return distances

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    predicted_ids = ["804", "101", "1010"]
    original_ids = ["1963", "1964", "679"]

    result = calculate_distances(predicted_ids, original_ids)
    
    for key, value in result.items():
        print(f"Predicted ID {key[0]}, Original ID {key[1]}: Distance {value[0]}, Path {value[1]}")
