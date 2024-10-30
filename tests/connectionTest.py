import unittest
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from graphDbWrapperClass import Neo4jWrapper
from neo4j.exceptions import ServiceUnavailable
import json
class TestNeo4jWrapper(unittest.TestCase):
    def setUp(self):
        with open("tests/credential.json", 'r') as config_file:
            config = json.load(config_file)
        self.uri = config.get("uri")
        self.auth = (config.get("username"),config.get("password"))

    def test_connection(self):
        try:
            driver = Neo4jWrapper.driver(self.uri, self.auth)
            driver.verify_connectivity()
            driver.close()
            self.assertTrue(True)  # If we get here, connection was successful
        except ServiceUnavailable:
            self.fail("Could not connect to Neo4j database")

    def test_execute_query(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        try:
            res, summary, keys = driver.execute_query("RETURN 1 AS num")
            self.assertEqual(res[0]['num'], 1)
        finally:
            driver.close()

if __name__ == '__main__':
    unittest.main()