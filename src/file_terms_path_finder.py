import gc
import sys
from UATMapper import UATMapper

def calculate_distances(predicted_ids, original_ids):
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()
    
    distances = {}

    for original_id in original_ids:
        for predicted_id in predicted_ids:
            # Find the shortest path between original and predicted
            shortest_path = thesaurus.find_shortest_path(original_id, predicted_id)

            if shortest_path and "1" not in shortest_path:
                # Save the distance and path if no '1' is present
                distances[(predicted_id, original_id)] = (len(shortest_path) - 1, shortest_path)
            else:
                # If no path is found or path contains '1', return None
                distances[(predicted_id, original_id)] = (0, "No path")
    
    return distances

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    
    predicted_ids = ["1145", "804", "486"]
    original_ids = ["343", "1383", "1338", "1345", "799"]

    result = calculate_distances(predicted_ids, original_ids)
    
    for key, value in result.items():
        print(f"Predicted ID {key[0]}, Original ID {key[1]}: Distance {value[0]}, Path {value[1]}")
