import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from graphDbWrapperClass import Neo4jWrapper
from neo4j.exceptions import ServiceUnavailable
from queryUpdate import update_query
import json
from filter import Filter


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
    driver.execute_query("CREATE (a:Course{name: 'COMP4336', assignment: 1, project_based: true, mode: 'Hybrid', year:4})")
    driver.execute_query("CREATE (a:Course{name: 'COMP3331',assignment: 3, project_based: false, mode: 'In-person', year:3})")
    driver.execute_query("CREATE (a:Course{name: 'COMP2500',assignment: 3, project_based: true, mode: 'Hybrid', year:2})") ## This does not exist in UNSW. Just for demo purpose
    driver.execute_query("CREATE (a:Course{name: 'COMP2521',assignment: 3, project_based: false, mode: 'In-person', year:2})")
    driver.execute_query("CREATE (a:Course{name: 'COMP1511',assignment: 3, project_based: false, mode: 'In-person', year:1})")
    driver.execute_query("CREATE (a:Course{name: 'COMP1531',assignment: 1, project_based: true, mode: 'Hybrid', year:1})")

    driver.execute_query("MATCH (a:Course{name: 'COMP4336'}), (b:Course{name: 'COMP3331'}) CREATE (a)-[:HAS_PREREQUISITE]->(b)")
    driver.execute_query("MATCH (a:Course{name: 'COMP4336'}), (b:Course{name: 'COMP2500'}) CREATE (a)-[:HAS_PREREQUISITE]->(b)")
    driver.execute_query("MATCH (a:Course{name: 'COMP3331'}), (b:Course{name: 'COMP2521'}) CREATE (a)-[:HAS_PREREQUISITE]->(b)")
    driver.execute_query("MATCH (a:Course{name: 'COMP2521'}), (b:Course{name: 'COMP1511'}) CREATE (a)-[:HAS_PREREQUISITE]->(b)")
    driver.execute_query("MATCH (a:Course{name: 'COMP2500'}), (b:Course{name: 'COMP1511'}) CREATE (a)-[:HAS_PREREQUISITE]->(b)")
    driver.execute_query("MATCH (a:Course{name: 'COMP1531'}), (b:Course{name: 'COMP1511'}) CREATE (a)-[:HAS_PREREQUISITE]->(b)")


    q = "MATCH (a:Course{name: 'COMP4336'})-[r:HAS_PREREQUISITE]->(b:Course) RETURN b.name"
    print("invoking the query: ", q)
    
    input("Press Enter to continue...")
    res, _, _ = driver.execute_query(q)
    #print res in red
    print("\033[91m")
    print(res)

    # make it back to normal color
    print("\033[0m")
    input("Press Enter to set up transitivity...")
    # setting up transitivity
    driver.update_transitive_relationship("HAS_PREREQUISITE", True)


    print("invoking the query: ", q)
    input("Press Enter to continue...")
    res2, _, _ = driver.execute_query(q)
    #print res2 in red
    print("\033[91m")
    print(res2)
    
    # make it back to normal color
    print("\033[0m")


    # setting up a filter
    myFilter = Filter()
    myFilter.set_filter("project_based", False)
    
    print("invoking the query: ", q)
    input("Press Enter to continue...")
    res3, _, _ = driver.execute_query(q, filter=myFilter)
    #print res3 in red
    print("\033[91m")
    print(res3)


    # setting up mode to be hybrid
    print("\033[0m")
    myFilter.set_filter("year", 1)
    print("invoking the query: ", q)
    input("Press Enter to continue...")
    res4, _, _ = driver.execute_query(q, filter=myFilter)
    #print res4 in red
    print("\033[91m")
    print(res4)