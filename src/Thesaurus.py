import heapq

class Thesaurus:
    def __init__(self, name):
        self.terms = {}
        self.name = name

    # Getters
    def get_by_id(self, term_id):
        return self.terms.get(term_id, None)

    def get_branch(self, term_id):
        root_term = self.get_by_id(term_id)
        branch_thesaurus = Thesaurus("branch" + root_term.get_name())
        branch_thesaurus.add_term(root_term)
        self.add_children_of_term(branch_thesaurus, root_term)
        return branch_thesaurus

    def get_size(self):
        return len(self.terms)

    def get_terms(self):
        return self.terms

    def get_by_name(self, name):
        for term in self.terms:
            if name == term.get_name():
                return term
            
    def get_active_fatherless_terms(self):
        fatherless_terms = []
        for term in self.terms.values():
            if len(term.get_parents()) == 0 and term.get_is_deprecated() == False:
                fatherless_terms.append(term.get_id())
        return fatherless_terms
    
    # Get the children of a term and recursively get the children of the children
    def get_branch_children(self, term_id):
        root_term = self.get_by_id(term_id)
        children = []
        for child_id in root_term.get_children():
            children.append(self.get_by_id(child_id))
            children += self.get_branch_children(child_id)
        return children

    # Setters
    def add_children_of_term(self, thesaurus, term):
        if len(term.get_children()) != 0:
            for child in term.get_children():
                child_term = self.get_by_id(child)
                self.add_children_of_term(thesaurus, child_term)
                thesaurus.add_term(child_term)

    def add_term(self, term):
        self.terms[term.get_id()] = term

    def print_names_and_ids(self):
        for term_key, term_value in self.terms.items():
            print("Id: ", term_key + " Name: " + term_value.get_name(), "Children: ", term_value.get_children())

    def find_shortest_path(self, start_id, end_id):
        if start_id not in self.terms or end_id not in self.terms:
            return None
        
        # Dijkstra initialization
        distances = {term_id: float('inf') for term_id in self.terms}
        distances[start_id] = 0
        previous = {term_id: None for term_id in self.terms}
        heap = [(0, start_id)]  # Heap de prioridad (distancia, term_id)

        # Dijkstra algorithm
        while heap:
            current_distance, current_id = heapq.heappop(heap)
            if current_id == end_id:
                break

            if current_distance > distances[current_id]:
                continue

            term = self.terms[current_id]

            # Update the distances to the children
            for child_id in term.children:
                new_distance = current_distance + 1  # Peso de 1 para todas las conexiones
                if new_distance < distances[child_id]:
                    distances[child_id] = new_distance
                    previous[child_id] = current_id
                    heapq.heappush(heap, (new_distance, child_id))

            # Update the distances to the parents
            for parent_id in term.parents:
                new_distance = current_distance + 1  # Peso de 1 para todas las conexiones
                if new_distance < distances[parent_id]:
                    distances[parent_id] = new_distance
                    previous[parent_id] = current_id
                    heapq.heappush(heap, (new_distance, parent_id))

        # Reconstruct the path
        path = []
        current_id = end_id
        while current_id:
            path.append(current_id)
            current_id = previous[current_id]

        path.reverse()
        return path if path[0] == start_id else None
