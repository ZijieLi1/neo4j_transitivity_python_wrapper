import unittest
import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from graphDbWrapperClass import Neo4jWrapper
from neo4j.exceptions import ServiceUnavailable
from queryUpdate import update_query
from filter import Filter
import json




# Dont worry about his file just for me to test things around

driver = Neo4jWrapper.driver("bolt://localhost:7687", ("neo4j","0000000000"))
driver.execute_query("MATCH ()-[r]-() DELETE r;")
driver.execute_query("MATCH (n) DELETE n")


# Create a relationship
driver.execute_query("CREATE (a:Person{name: 'Tom'})")
driver.execute_query("CREATE (a:Person{name: 'Jerry', gender: True})")
driver.execute_query("CREATE (a:Person{name: 'Spike', gender: 'female'})")
driver.execute_query("MATCH (a:Person{name: 'Tom'}), (b:Person{name: 'Jerry'}) CREATE (a)-[:TALLER_THAN]->(b)")
driver.execute_query("MATCH (a:Person{name: 'Jerry'}), (b:Person{name: 'Spike'}) CREATE (a)-[:TALLER_THAN]->(b)")

driver.update_transitive_relationship("TALLER_THAN", True)
print("DB INFO ==========================================================")
transitivities = driver.get_all_transitivity()

# Query the database
myFilter = Filter()
myFilter.set_filter("gender", True)

q = "MATCH (a:Person{name: 'Tom'})-[:TALLER_THAN]->(b:Person) RETURN b.name"
print("invoking the query: ", q)
res, _, _ = driver.execute_query(q, filter = myFilter)
print(res)
