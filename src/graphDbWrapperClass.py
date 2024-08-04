from neo4j import GraphDatabase, Driver
from driverWrapper import driver_init

class Neo4jWrapper(GraphDatabase):
    def driver(uri: str, auth: tuple):
        driver = GraphDatabase.driver(uri, auth=auth)
        return driver_init(driver)



