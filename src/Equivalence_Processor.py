# Imports
from obj_tree import tree

class Equivalence_Processor():
    
    def __init__(self):
        # Initialize similarity measurment values
        self.sim = 0
        self.diff_val = 0
        
        # Initialize trees to null
        self.tree_a = None
        self.tree_b = None
        
    def compare_json_objs(self, comparison):
        
        # Direct equivalence check
        if comparison.json_object_a != comparison.json_object_b:
            # Calculate how similar they are, if at all. 
            print("JSON files not exactly the same.")
            self.compare_objects(comparison)
            total = self.sim + self.diff_val
            return self.sim / total if total > 0 else 0
            
        else: 
            self.compare_objects(comparison)
            print("JSON files are exactly the same.")
            # The JSON objects are 100% equivalent 
            return 1

    # Takes in a Comparison object and goes through it's json objects
    def compare_objects(self, comparison):
        obj_a = comparison.json_object_a
        obj_b = comparison.json_object_b
        
        # lists for keeping track of the current object value's states for comparison
        self.tree_a = tree(obj_a)
        self.tree_b = tree(obj_b)
        
        self.traverse_trees()

        # Split stats print:
        atomic_values_a, list_count_a, dict_count_a, node_count_a = self.tree_a.get_values()
        atomic_values_b, list_count_b, dict_count_b, node_count_b = self.tree_b.get_values()
        
        print("Node count: A;", node_count_a, "B;", node_count_b)
        print("Atomic value count: A;", atomic_values_a, "B;", atomic_values_b)
        print("List count: A;", list_count_a, "B;", list_count_b)
        print("Dictionary Count: A;", dict_count_a, "B;",dict_count_b)
        
        total = self.sim + self.diff_val
        print("Similar:", self.sim)
        print("Total:", total)
        print("Percent Similarity:", str(round((self.sim/total)*100, 2))+"%")
        
            
    def traverse_trees(self):
        
        # We are done traversing the trees when the root nodes are both visited.
        while (not self.tree_a.root_visited()) and (not self.tree_b.root_visited()):
            if self.tree_a.get_next_node().is_visited():
                self.tree_a.set_next_as_parent()
                self.tree_b.set_next_as_parent()

            if self.node_comparison(self.tree_a.get_next_node(), self.tree_b.get_next_node()):
                # If true, we need to go a layer deeper. So we go inside the current set of nodes, and evaluate their children.
                # Choose the first child that has not been visited.
                    
                for child in self.tree_a.get_next_node().get_children():
                    if not child.is_visited():
                        self.tree_a.set_next_node(child)
                        break
                        
                for child in self.tree_b.get_next_node().get_children():
                    if not child.is_visited():
                        self.tree_b.set_next_node(child)
                        break
            
            else:
                # If false, it has evaluated somehow. So we set the next node to the current node's parent.
                if (self.tree_a.get_next_node().get_parent() is not None) and (self.tree_b.get_next_node().get_parent() is not None):
                    self.tree_a.set_next_as_parent()
                    self.tree_b.set_next_as_parent()
                    self.visitation_check()


    def visitation_check(self):
        # After updating the next node, we check if it should be set to visited (if all it's children are visited)
        visit_check_a = True
        for child in self.tree_a.get_next_node().get_children():
            if not child.is_visited():
                visit_check_a = False
                break
                # ERROR IN HERE???
        visit_check_b = True
        for child in self.tree_b.get_next_node().get_children():
            if not child.is_visited():
                visit_check_b = False
                break

        # If one node is set to visited, the other node should also be set to visited, and if it has any remaining children, they should be accounted for by adding their values to diff_val.
        if (not visit_check_a) and (not visit_check_b):
            # Don't set either to visited.
            pass
        elif visit_check_a and visit_check_b:
            # Both are visited fully
            self.tree_b.get_next_node().set_visited()
            self.tree_a.get_next_node().set_visited()
        else:
            # Only one was finished being visited, which means we use the remaining children of the other node for their values and set it to visited anyway.
            if visit_check_a:
                for child in self.tree_b.get_next_node().get_children():
                    if not child.is_visited():
                        self.diff_val += child.get_total()
            else:
                for child in self.tree_a.get_next_node().get_children():
                    if not child.is_visited():
                        self.diff_val += child.get_total()

            self.tree_b.get_next_node().set_visited()
            self.tree_a.get_next_node().set_visited()
                    
                    
    # Adds the node's compared value to the totals, and returns whether or not the nodes need to be explored deeper.
    def node_comparison(self, node_a, node_b):
        # Checks if the nodes are equivalent
        if node_a.get_var() == node_b.get_var():
            # Adds the nodes of tree a to similarity value
            self.sim += node_a.get_total()
            
            # Mark both nodes as visited.
            node_a.set_visited()
            node_b.set_visited()
            return False
        
        # Checks if the nodes have a type difference
        elif node_a.get_node_type() is not node_b.get_node_type():
            return self.evaluate_type_diff(node_a, node_b)
        
        # Checks if the nodes values are different but they are of the same type.
        else:
            # Evaluates the difference between nodes of the same type.
            return self.evaluate_diff(node_a, node_b)
    
    # Evaluates the difference between two nodes of differing types.
    def evaluate_type_diff(self, node_a, node_b):
        # Checks if the nodes are both of atomic typing
        if node_a.type_check() == -1 and node_b.type_check() == -1:
            self.diff_val += 1
        elif node_a.type_check() == -1 or node_b.type_check() == -1:
            # Use the dict/list node to determine the amount of miss matches to add
            if node_a.type_check() == -1:
                self.diff_val += node_b.get_total()
            else: 
                self.diff_val += node_a.get_total()
        else:   # Both nodes are of type dict/list
            # Use both nodes values to determine amount of mis matches, but subtract 1 for the intial node mismatch
            self.diff_val += node_a.get_total() + node_b.get_total() - 1
        
        # Set both nodes as visited, as we won't need to explore them deeper.
        node_a.set_visited()
        node_b.set_visited()
        return False
        
    # Evaluates the difference between two nodes of the same typing.
    def evaluate_diff(self, node_a, node_b):
        # Checks if the nodes are atomic, meaning they just have different values.
        if node_a.type_check() == -1 and node_b.type_check() == -1 and not node_a.is_evaluated():
            # Add 1 to diff, mark both as visited.
            self.diff_val += 1
            node_a.set_visited()
            node_b.set_visited()
            node_a.set_evaluated()
            node_b.set_evaluated()
        else: # Both are of either type 'DICT' or 'LIST'
            # Add 1 to similarity, as these nodes technically match, the only difference is the children nodes.
            if not node_a.is_evaluated():
                self.sim += 1
                node_a.set_evaluated()
                node_b.set_evaluated()
            self.visitation_check()

            if len(node_a.get_children()) > 0 and len(node_b.get_children()) > 0:
                # Signal to go deeper into these nodes
                return True
            elif len(node_a.get_children()) > 0:
                # Node b is an empty dict/list, so we add the value of node a minus 1 to the total diff value.
                self.diff_val += node_a.get_total()-1
                node_a.set_visited()
                node_b.set_visited()
            else:
                # Node a is an empty dict/list, so we add the value of node a minus 1 to the total diff value.
                self.diff_val += node_b.get_total()-1
                node_a.set_visited()
                node_b.set_visited()

            return False