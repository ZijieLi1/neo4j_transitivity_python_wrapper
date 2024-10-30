import unittest
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from graphDbWrapperClass import Neo4jWrapper
from neo4j.exceptions import ServiceUnavailable
import json


class TestRelManage(unittest.TestCase):
    def setUp(self):
        with open("tests/credential.json", 'r') as config_file:
            config = json.load(config_file)
        self.uri = config.get("uri")
        self.auth = (config.get("username"),config.get("password"))

    def test_node_del(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("MATCH (n:TMetadata) DELETE n")
        x = driver.get_all_transitivity()
        assert x == []
        # if we try to add the rel, it should recreate the meta node.
        driver.update_transitive_relationship("LESS_THAN", True)
        x = driver.get_all_transitivity()
        assert x == ['LESS_THAN']
        driver.remove_all_transitivity()


    def test_rel_add_remove(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        x = driver.get_all_transitivity()
        assert x == []
        driver.update_transitive_relationship("LESS_THAN", True)
        assert len(driver.get_all_transitivity()) == 1
        driver.update_transitive_relationship("MORE_THAN", True)
        assert len(driver.get_all_transitivity()) == 2

        driver.update_transitive_relationship("LESS_THAN", False)
        assert len(driver.get_all_transitivity()) == 1
        assert driver.get_all_transitivity() == ['MORE_THAN']
        driver.remove_all_transitivity()

    def test_add_dup(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.update_transitive_relationship("LESS_THAN", True)
        driver.update_transitive_relationship("LESS_THAN", True)
        assert len(driver.get_all_transitivity()) == 1
        # make sure remove works after attmpting to add dup
        driver.update_transitive_relationship("LESS_THAN", False)
        assert len(driver.get_all_transitivity()) == 0
        driver.remove_all_transitivity()

    def test_remove_non_exist(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.update_transitive_relationship("LESS_THAN", True)
        assert len(driver.get_all_transitivity()) == 1
        driver.update_transitive_relationship("abc", False)
        assert len(driver.get_all_transitivity()) == 1
        driver.remove_all_transitivity()
if __name__ == '__main__':
    unittest.main()