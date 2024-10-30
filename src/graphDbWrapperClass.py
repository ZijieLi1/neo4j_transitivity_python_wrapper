from neo4j import GraphDatabase, Driver
from driverWrapper import driver_init

class Neo4jWrapper(GraphDatabase):
    def driver(uri: str, auth: tuple):
        driver = GraphDatabase.driver(uri, auth=auth)
        return driver_init(driver)



if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    auth = ("neo4j", "0000000000")
