import json
from typing import Dict, Any

class Filter():
    def __init__(self):
        self.filters = {}
    def set_filter(self, label: str, value:str):
        """Set property filters for specific node labels."""
        self.filters[label] = value
    def remove_filter(self, label: str):
        """Remove property filters for specific node labels."""
        if label in self.filters:
            del self.filters[label]
    def list_filters(self):
        return self.filters
    def set_filter_from_file(self, file_path: str):
        with open(file_path, 'r') as file:
            self.filters = json.load(file)

    def create_condition_clause(self, node_name):
        """Create a condition clause for the node."""
        clause = ""
        for x in self.filters:
            value = self.filters[x]
            clause += f"{node_name}.{x} = {self.value_parsing(value)} AND "
        return clause[:-5]


    def value_parsing(self, value):
        if isinstance(value, str):
            return f"'{value}'"
        else :
            return value
 
    