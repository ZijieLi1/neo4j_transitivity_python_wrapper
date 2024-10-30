import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from graphDbWrapperClass import Neo4jWrapper
from neo4j.exceptions import ServiceUnavailable
from queryUpdate import update_query
import json



if __name__ == '__main__':
    # Create the driver object connect to the database
    cleanupdriver = Neo4jWrapper.driver("bolt://localhost:7687", ("neo4j","0000000000"))
    # Clear the database
    cleanupdriver.execute_query("MATCH ()-[r]-() DELETE r;")
    cleanupdriver.execute_query("MATCH (n) DELETE n")
    cleanupdriver.remove_all_transitivity()
    print("DB initialized with no data")

    driver = Neo4jWrapper.driver("bolt://localhost:7687", ("neo4j","0000000000"))

    # Create a relationship
    driver.execute_query("CREATE (a:Person{name: 'Tom'})")
    driver.execute_query("CREATE (a:Person{name: 'Jerry'})")
    driver.execute_query("CREATE (a:Person{name: 'Spike'})")
    driver.execute_query("MATCH (a:Person{name: 'Tom'}), (b:Person{name: 'Jerry'}) CREATE (a)-[:TALLER_THAN]->(b)")
    driver.execute_query("MATCH (a:Person{name: 'Jerry'}), (b:Person{name: 'Spike'}) CREATE (a)-[:TALLER_THAN]->(b)")

    print("DB INFO ==========================================================")
    transitivities = driver.get_all_transitivity()
    print(f"transtive rel: {json.dumps(transitivities, indent=4)}")
    print(f"current data: Tom -> Jerry -> Spike")
    # Query the database
    print()
    q = "MATCH (a:Person{name: 'Tom'})-[r:TALLER_THAN]->(b:Person) RETURN b.name"
    print("invoking the query: ", q)
    input()
    res, _, _ = driver.execute_query(q)
    print(res)
    input()

    # Update the relationship
    driver.update_transitive_relationship("TALLER_THAN", True)
    print("DB INFO ==========================================================")
    transitivities = driver.get_all_transitivity()
    print(f"transtive rel: {json.dumps(transitivities, indent=4)}")
    print(f"current data: Tom -> Jerry -> Spike")

    # Query the database
    q = "MATCH (a:Person{name: 'Tom'})-[:TALLER_THAN]->(b:Person) RETURN b.name"
    print("invoking the query: ", q)
    input()
    res2, _, _ = driver.execute_query(q)
    print(res2)
    input()

    
    #update the database so it will seperate into two branch
    driver.execute_query("CREATE (:Person{name: 'Alice'})")
    driver.execute_query("CREATE (:Person{name: 'Ada'})")
    driver.execute_query("MATCH (a:Person{name: 'Spike'}), (b:Person{name: 'Alice'}) CREATE (a)-[:TALLER_THAN]->(b)")
    driver.execute_query("MATCH (a:Person{name: 'Spike'}), (b:Person{name: 'Ada'}) CREATE (a)-[:TALLER_THAN]->(b)")
    print("DB INFO ==========================================================")
    print(f"""                      
                                        -> Alice
          current data: Tom -> Jerry -> Spike
                                        -> Ada
          """)
    transitivities = driver.get_all_transitivity()

    q = "MATCH (a:Person{name: 'Tom'})-[:TALLER_THAN]->(b:Person) RETURN b.name"
    print("invoking the query: ", q)
    input()
    res3, _, _ = driver.execute_query(q)
    print(res3)
    input()

    # execute query with distance exact 1
    q = "MATCH (a:Person{name: 'Tom'})-[:TALLER_THAN*1]->(b:Person) RETURN b.name"
    print("invoking the query: ", q)
    input()
    res3, _, _ = driver.execute_query(q)
    print(res3)
    input()


    # execute query with distance less than 2
    q = "MATCH (a:Person{name: 'Tom'})-[:TALLER_THAN*..2]->(b:Person) RETURN b.name"
    print("invoking the query: ", q)
    input()
    res3, _, _ = driver.execute_query(q)
    print(res3)
    input()


    # broke the transitivity
    driver.execute_query("MATCH (a:Person{name: 'Jerry'})-[r]->(b:Person{name: 'Spike'}) DELETE r")
    print("DB INFO ==========================================================")
    print(f"""                      
                                          -> Alice
          current data: Tom -> Jerry  Spike
                                          -> Ada
          """)
    q = "MATCH (a:Person{name: 'Tom'})-[:TALLER_THAN]->(b:Person) RETURN b.name"
    print("invoking the query: ", q)
    input()
    res3, _, _ = driver.execute_query(q)
    print(res3)