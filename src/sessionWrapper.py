from queryUpdate import update_query
from driverRelManagerClass import driverRelManager



def wrap_run(original_query, rel_manager=None):
    def new_query(*args, **kwargs):
        query = args[0] if args else kwargs.get('query')
        if query:
            updated_query = update_query(query,rel_manager=rel_manager)
            return original_query(updated_query, *args[1:], **kwargs)
        return original_query(*args, **kwargs)
    return new_query


def session_init(session, rel_manager=None):

    # this will be the function replace driver.session()
    def wrapper_session_init(*args, **kwargs):
        orginal_session_obj = session(*args, **kwargs)
        orginal_session_obj.run = wrap_run(orginal_session_obj.run, rel_manager)

        return orginal_session_obj


    return wrapper_session_init