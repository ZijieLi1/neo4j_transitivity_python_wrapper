import unittest
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from graphDbWrapperClass import Neo4jWrapper
from neo4j.exceptions import ServiceUnavailable
from filter import Filter
import json


class TestFilter(unittest.TestCase):
    def setUp(self):
        with open("tests/credential.json", 'r') as config_file:
            config = json.load(config_file)
        self.uri = config.get("uri")
        self.auth = (config.get("username"),config.get("password"))
        self.data_clean()

    def data_clean(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("MATCH ()-[r]-() DELETE r;")
        driver.execute_query("MATCH (n) DELETE n")
        
    def test_clause_build(self):
        filter = Filter()
        filter.set_filter("gender", "male")
        filter.set_filter("height", 122)
        filter.set_filter("married", False)
        print(filter.create_condition_clause("n"))
        assert filter.create_condition_clause("n") == "n.gender = 'male' AND n.height = 122 AND n.married = False"




if __name__ == '__main__':
    unittest.main()