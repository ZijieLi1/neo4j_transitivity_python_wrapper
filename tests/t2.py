import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from filter import Filter
# Dont worry about his file just for me to test things around
filter = Filter()
filter.set_filter("gender", "male")
filter.set_filter("height", 122)
filter.set_filter("married", False)
print(filter.create_condition_clause("n"))