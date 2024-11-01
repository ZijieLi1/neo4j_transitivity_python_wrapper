from queryUpdate import update_query
from driverRelManagerClass import driverRelManager
from sessionWrapper import session_init
import json

def wrap_execute_query(original_query, rel_manager=None):
    def new_query(*args, **kwargs):
        query = args[0] if args else kwargs.get('query')
        filter = kwargs.get('filter', None)
        if query:
            updated_query = update_query(query,rel_manager=rel_manager, filter = filter)
            # remove filter from **kwargs
            if 'filter' in kwargs:
                del kwargs['filter']
            return original_query(updated_query, *args[1:], **kwargs)
        return original_query(*args, **kwargs)
    return new_query

def driver_init(neo4j_driver):
    original_execute_query = neo4j_driver.execute_query
    
    rel_manager = driverRelManager(neo4j_driver, cached=True)


    neo4j_driver.is_transitive = rel_manager.is_transitive
    neo4j_driver.update_transitive_relationship = rel_manager.update_transitive_relationship
    neo4j_driver.get_all_transitivity = rel_manager.get_all_transitivity
    neo4j_driver.remove_all_transitivity = rel_manager.remove_all_transitivity
    
    # order matters. wrap_execute_query should be the last one. so the driver can use use rel_manager.is_transitive

    neo4j_driver.execute_query = wrap_execute_query(original_execute_query,rel_manager=rel_manager)

    # overwrite the session to make sure the driver is not using the default session but the one with the updated execute_query

    neo4j_driver.session = session_init(neo4j_driver.session, rel_manager= rel_manager)
    
    return neo4j_driver