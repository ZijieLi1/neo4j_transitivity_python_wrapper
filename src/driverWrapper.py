def wrap_execute_query(original_query):
    def new_query(*args, **kwargs):
        
        query = args[0] if args else kwargs.get('query')
        return original_query(*args, **kwargs)
    return new_query

def driver_init(neo4j_driver):
    original_execute_query = neo4j_driver.execute_query
    neo4j_driver.execute_query = wrap_execute_query(original_execute_query)
    return neo4j_driver