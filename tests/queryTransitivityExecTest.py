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
        self.data_clean()

    def data_clean(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("MATCH ()-[r]-() DELETE r;")
        driver.execute_query("MATCH (n) DELETE n")
        
    def test_simple_query(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        # insert two nodes n1,n2 and n1 -> n2
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("MATCH (n1:Number {number: 1}) CREATE (n1)-[:LESS_THAN]->(n2:Number {number: 2})")
        # query for n2
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 1
        self.data_clean()

    # test the case 1 < 2, and 2<3. It should return 2 and 3 given transitivity
    """
    1 --> 2 --> 3
    """
    def test_linear_transitivity(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:LESS_THAN]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:LESS_THAN]->(n3);")
        driver.update_transitive_relationship("LESS_THAN", True)
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 2
        assert records[0]['greater']['number'] == 2
        assert records[1]['greater']['number'] == 3
        self.data_clean()

    '''
            ->3
    1 -> 2
            ->4
    '''
    def test_branch_transitivity(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("CREATE (n3: Number {number: 4})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:LESS_THAN]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:LESS_THAN]->(n3);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n4:Number {number: 4})CREATE (n2)-[:LESS_THAN]->(n4);")
        driver.update_transitive_relationship("LESS_THAN", True)
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 3
        # make sure the res is 2,3,4
        my_set = set()
        for i in records:
            my_set.add(i['greater']['number'])
        assert 2 in my_set
        assert 3 in my_set
        assert 4 in my_set
        self.data_clean()

    def test_query_already_distance_infinity(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:LESS_THAN]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:LESS_THAN]->(n3);")
        # this already use * so should still work even not transitive
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN*]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 2
        assert records[0]['greater']['number'] == 2
        assert records[1]['greater']['number'] == 3
        self.data_clean()

    def test_loop(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:SAME_TYPE]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:SAME_TYPE]->(n3);")
        driver.execute_query("MATCH (n3:Number {number: 3}), (n1:Number {number: 1})CREATE (n3)-[:SAME_TYPE]->(n1);")
        driver.update_transitive_relationship("SAME_TYPE", True)
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:SAME_TYPE]->(same:Number) RETURN DISTINCT same;")
        assert len(records) == 3
        assert records[0]['same']['number'] == 2
        assert records[1]['same']['number'] == 3
        self.data_clean()

    def test_with_lower_bound_distance(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("CREATE (n4: Number {number: 4})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:LESS_THAN]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:LESS_THAN]->(n3);")
        driver.execute_query("MATCH (n3:Number {number: 3}), (n4:Number {number: 4}) CREATE (n3)-[:LESS_THAN]->(n4);")

        driver.update_transitive_relationship("LESS_THAN", True)
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN*2..]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 2
        assert records[0]['greater']['number'] == 3
        assert records[1]['greater']['number'] == 4
        self.data_clean()

    def test_with_upper_bound_distance(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("CREATE (n4: Number {number: 4})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:LESS_THAN]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:LESS_THAN]->(n3);")
        driver.execute_query("MATCH (n3:Number {number: 3}), (n4:Number {number: 4}) CREATE (n3)-[:LESS_THAN]->(n4);")

        driver.update_transitive_relationship("LESS_THAN", True)
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN*..2]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 2
        assert records[0]['greater']['number'] == 2
        assert records[1]['greater']['number'] == 3
        self.data_clean()

    def test_with_distance_0(self):
        driver = Neo4jWrapper.driver(self.uri, self.auth)
        driver.execute_query("CREATE (n1: Number {number: 1})")
        driver.execute_query("CREATE (n2: Number {number: 2})")
        driver.execute_query("CREATE (n3: Number {number: 3})")
        driver.execute_query("CREATE (n4: Number {number: 4})")
        driver.execute_query("MATCH (n1:Number {number: 1}), (n2:Number {number: 2}) CREATE (n1)-[:LESS_THAN]->(n2);")
        driver.execute_query("MATCH (n2:Number {number: 2}), (n3:Number {number: 3})CREATE (n2)-[:LESS_THAN]->(n3);")
        driver.execute_query("MATCH (n3:Number {number: 3}), (n4:Number {number: 4}) CREATE (n3)-[:LESS_THAN]->(n4);")

        driver.update_transitive_relationship("LESS_THAN", True)
        records, summary, keys = driver.execute_query("MATCH path = (n1:Number {number: 1})-[:LESS_THAN*0..1]->(greater:Number) RETURN DISTINCT greater;")
        assert len(records) == 2
        assert records[0]['greater']['number'] == 1
        assert records[1]['greater']['number'] == 2
        self.data_clean()
if __name__ == '__main__':
    unittest.main()