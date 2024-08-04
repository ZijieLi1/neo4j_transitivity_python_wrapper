class driverRelManager():
    def __init__(self, driver):
        self.driver = driver
        if not self.meta_node_exists():
            self.create_meta_node()


    def create_meta_node(self):
        query = f"""
        CREATE (m:TMetadata {{nameList: []}})
        RETURN m
        """
        self.driver.execute_query(query)

    def meta_node_exists(self):
        query = f"""
        MATCH (m:TMetadata)
        RETURN m
        """
        records, summary, keys = self.driver.execute_query(query)
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
        RETURN m
        """
        self.driver.execute_query(query)

    def remove_transitive_relationship(self, rel_name):
        x = self.get_all_transitivity()
        # only need to remove the left most occurance since the list is unique
        x.remove(rel_name)
        
        # update the list
        query = f"""
        MATCH (m:TMetadata)
        SET m.nameList = {x}
        RETURN m
        """
        self.driver.execute_query(query)

    def is_transitive(self, rel_name):
        query = f"""
        MATCH (m:TMetadata)
        RETURN '{rel_name}' IN m.nameList AS nameExists
        """
        records, summary, keys = self.driver.execute_query(query)
        
        # Check if the name exists in the database. return False for the case of keyerror, eg, when meta node does not exist or no driver connections.
        try:
            return records[0]['nameExists']
        except Exception as e:
            return False
        
    def get_all_transitivity(self):
        query = f"""
        MATCH (m:TMetadata)
        RETURN m.nameList
        """
        records, summary, keys = self.driver.execute_query(query)

        # handle the case where there is no metadata node
        if not records:
            return []
        return records[0]['m.nameList']
    
    def remove_all_transitivity(self):
        query = f"""
        MATCH (m:TMetadata)
        SET m.nameList = []
        RETURN m
        """
        self.driver.execute_query(query)