class driverRelManager():
    def __init__(self, driver, cached = True):
        self.driver = driver
        if not self.meta_node_exists():
            self.create_meta_node()

        self.cached = cached
        self.last_cached = -1
        # if cached:
        #     self.cached_transitivity = self.get_all_transitivity()


    def create_meta_node(self):
        print("creating meta node")
        query = f"""
        CREATE (m:TMetadata {{nameList: [], last_update: 0}})
        RETURN m
        """
        self.driver.execute_query(query, filter = None)

    def meta_node_exists(self):
        query = f"""
        MATCH (m:TMetadata)
        RETURN m
        """
        records, summary, keys = self.driver.execute_query(query, filter = None)
        return len(records) > 0
    def update_transitive_relationship(self, rel_name, is_transitive = True):
        if not self.meta_node_exists():
            self.create_meta_node()

        if is_transitive:
            if not self.is_transitive(rel_name):
                self.add_transitive_relationship(rel_name)
        else:
            if self.is_transitive(rel_name):
                self.remove_transitive_relationship(rel_name)
    
    def add_transitive_relationship(self, rel_name):
        query = f"""
        MATCH (m:TMetadata)
        SET m.nameList = m.nameList + ['{rel_name}']
        SET m.last_update = m.last_update + 1
        RETURN m
        """
        self.driver.execute_query(query, filter = None)

    def remove_transitive_relationship(self, rel_name):
        x = self.get_all_transitivity()
        # only need to remove the left most occurance since the list is unique
        x.remove(rel_name)
        
        # update the list
        query = f"""
        MATCH (m:TMetadata)
        SET m.nameList = {x}
        SET m.last_update = m.last_update + 1
        RETURN m
        """
        self.driver.execute_query(query, filter = None)

    def is_transitive(self, rel_name):
        if self.cached:
            self.cached_up_to_date()
            return rel_name in self.cached_transitivity
            
        print("not cached")
        query = f"""
        MATCH (m:TMetadata)
        RETURN '{rel_name}' IN m.nameList AS nameExists
        """
        records, summary, keys = self.driver.execute_query(query, filter = None)
        
        # Check if the name exists in the database. return False for the case of keyerror, eg, when meta node does not exist or no driver connections.
        try:
            return records[0]['nameExists']
        except Exception as e:
            return False
        
    def get_all_transitivity(self):
        if not self.meta_node_exists():
            self.create_meta_node()
        query = f"""
        MATCH (m:TMetadata)
        RETURN m.nameList
        """
        records, summary, keys = self.driver.execute_query(query, filter = None)

        # handle the case where there is no metadata node
        if not records:
            return []
        return records[0]['m.nameList']
    
    def remove_all_transitivity(self):
        query = f"""
        MATCH (m:TMetadata)
        SET m.nameList = []
        SET m.last_update = m.last_update + 1
        RETURN m
        """
        self.driver.execute_query(query, filter = None)

    def cached_up_to_date(self):
        # check if last update is the same as the last cached
        query = f"""
        MATCH (m:TMetadata)
        RETURN m.last_update
        """
        records, summary, keys = self.driver.execute_query(query, filter = None)
        last_update = records[0]['m.last_update']
        if last_update != self.last_cached:
            print("last update: ", last_update, "last cached: ", self.last_cached)
            print("updating cache")
            self.cached_transitivity = self.get_all_transitivity()
            self.last_cached = last_update
            print("cache updated", "set last cached to: ", self.last_cached)
