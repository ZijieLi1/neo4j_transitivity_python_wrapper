import unittest
from src.queryUpdate import update_query

import sys
import os
# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))



class TestQueryUpdate(unittest.TestCase):

    def test_simple_relationships(self):
        query = "MATCH (a)-[KNOS]->(b)-[r2:KNOWS]->(c) RETURN a,b,c"
        expected = "MATCH (a)-[KNOS*]->(b)-[r2:KNOWS*]->(c) RETURN a,b,c"
        self.assertEqual(update_query(query,True), expected)

    def test_complex_relationships(self):
        query = "MATCH (n1:Number {number: 1})-[:LESS_THAN*]->(greater:Number)<-[:LESS_THAN]-(n2:Number {number: 2}) RETURN DISTINCT greater;"
        expected = "MATCH (n1:Number {number: 1})-[:LESS_THAN*]->(greater:Number)<-[:LESS_THAN*]-(n2:Number {number: 2}) RETURN DISTINCT greater;"
        self.assertEqual(update_query(query,True), expected)

    def test_one_character_relationship(self):
        query = "MATCH (a)-[K]->(b) RETURN a, b"
        expected = "MATCH (a)-[K*]->(b) RETURN a, b"
        self.assertEqual(update_query(query,True), expected)

    def test_no_relationships(self):
        query = "RETURN a, b, c"
        expected = "RETURN a, b, c"
        self.assertEqual(update_query(query,True), expected)

    def test_mixed_case_keywords(self):
        query = "match (a)-[KnOS]->(b) return a, b"
        expected = "match (a)-[KnOS*]->(b) return a, b"
        self.assertEqual(update_query(query,True), expected)

    def test_path(self):
        query = """
        MATCH path = (n1:Number {number: 1})-[:LESS_THAN]->(greater:Number)
        RETURN DISTINCT greater;
        """
        excepted = "MATCH path = (n1:Number {number: 1})-[:LESS_THAN*]->(greater:Number) RETURN DISTINCT greater;"

        self.assertEqual(update_query(query,True), excepted)
if __name__ == '__main__':
    unittest.main()