# import the itertools function, so I dont have to manually create them
import itertools
# Some sources used:
# https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
# https: // stackoverflow.com / questions / 3462143 /
# get - difference - between - two - lists
# http: // old.sztaki.hu / ~fodroczi / dbs / dep - pres - own.pdf
# https: // wiki.python.org / moin / HowTo / Sorting
# https: // stackoverflow.com / questions / 19371358 /
# python - typeerror - unhashable - type - list
# https: // stackoverflow.com / questions / 6593979 /
# how - to - convert - a - set - to - a - list - in -python
# https: // stackoverflow.com / questions / 16579085 / python
# https://stackoverflow.com/questions/18623871/python-and-
# - verifying - if -one - list - is -a - subset - of - the - other
# https: // www.programiz.com / python - programming / methods / set / issubset


# Declare attributes as a set to remove duplicates
# Dependencies will later be formatted to remove duplicates
# Easier to do than remove duplicates after each addition
# All parameters will be case sensitive
# May have some inheritance properties
class FunctionalDependencySet:
    def __init__(self, attributes, name):
        self.dependencies = []
        self.keys = []
        self.all_tables = []
        self.decomp_keys = []
        self.attributes = set()
        self.name = name

        # initialize the attributes
        # Needed for the set
        self.add_attributes(attributes)

    # Assuming that the provided attributes are in a nested list format
    # Add the attributes to the class
    def add_attributes(self, attributes):
        for attribute in attributes:
            for a in attribute:
                self.attributes.add(a)

    # Expected format of dependency_list is [['key1', 'key2'], ['attribute1', 'attribute2']]
    # No need for this to be a part of init
    def add_dependency(self, dependency_list):
        dependency = self.format_dependency(dependency_list)
        self.dependencies.append(dependency)
        self.keys.append(dependency_list[0])
        return 0

    # Expected format of dependency is [['key1', 'key2'], ['attribute1', 'attribute2']]
    # dependency will always be a nested loop
    # will return a set nested within a loop, original order is destroyed as are duplicates
    def format_dependency(self, dependency_list):
        temp = []
        for dependency in dependency_list:
            dependency = set(dependency)
            temp.append(dependency)
        return temp

    # Simple get to get the keys of a program
    # Remove duplicates from the nested loop
    def get_keys(self):
        fset = set(frozenset(x) for x in self.keys)
        beter = [list(x) for x in fset]
        return beter

    # Getter for the name
    def get_name(self):
        return self.name

    # Sort the attributes, stored as 1D set
    def sort_attributes(self):
        return sorted(self.attributes)

    # Sort the keys, store as a 2D list
    def sort_keys(self):
        newlist = map(sorted, self.keys)
        return list(newlist)

    # Used to remove duplicates
    def remove(self):
        decomp = self.decompose()
        somelist = [x for x in decomp if set()]
        return somelist

    # Check for a subset
    # set_a is the smaller set
    def contains(self, set_a, set_b):
        if all(a in set_b for a in set_a):
            return True
        else:
            return False

    # Function to find the candidate keys
    # Uses a recursive and loop approach to find the closure of elements
    def find_candidate_keys(self):
        temp = []
        min_keys_for_len = []
        possible_keys = []
        duplicates_removed = []
        final = []
        total_attributes = len(self.attributes) + 1
        i = 1
        while i < total_attributes:

            all_combinations = self.formatted_combinations(self.attributes, i)
            max_index = len(all_combinations)

            # Recursive call that finds the minimum keys required, for a given length
            possible_keys = self.find_minimum_key_recur(all_combinations, 0, max_index, min_keys_for_len)
            temp = self.find_minimum_key_loop(temp, i)

            i += 1

        # Try to find consistency between the loop and recursive calls
        # Firstly, remove duplicates by making it into a set
        for key in possible_keys:
            duplicates_removed.append(set(key))

        for i in duplicates_removed:
            for j in temp:
                if i == j:
                    final.append(j)

        # Get the candidate keys
        # Append then to the keys of the class
        # We will use these later
        self.keys.append(list(final[0]))
        return final

    # Looping method to find possible keys
    # Same logic as the rcursive implementation, but retrieves fewer possible keys
    def find_minimum_key_loop(self, loop_list, i):
        beter = self.formatted_combinations(self.attributes, i)
        total = len(beter) -1
        done = False
        index = 0

        # Continue iteration until all possibiities for combinations of len i have been exhausted
        while not done:
            if index == total:
                done = True

            if self.is_candidate_key(beter[index]):
                k = set(beter[index])
                if not any([x.issubset(k) for x in loop_list]):
                    loop_list.append(k)
            index += 1

        return loop_list

    # Recursion to find minimum possible keys
    # Max index is used instead of a bool, as I needed the precise location of the key
    # Continue recursion so long that indices are still the same
    def find_minimum_key_recur(self, all_combinations, index, max_index, min_keys_for_len):

        while index < max_index:
            if self.is_candidate_key(all_combinations[index]):
                min_keys_for_len.append(all_combinations[index])
            index += 1
            return self.find_minimum_key_recur(all_combinations, index, max_index, min_keys_for_len)

        return min_keys_for_len

    # Function used to check if the closure of a key is equal to the attributes
    # Returns true if so, false otherwise
    # Conversion of closure into a set is for a safe measure
    def is_candidate_key(self, candidate_key):
        closure = self.get_closure(candidate_key)
        closure = set(closure)
        if closure != self.attributes:
            return False
        else:
            return True

    # Compute the closure of an attribute
    # Attr is just a list
    def get_closure(self, attr):
        closure_of = set(attr)
        check_set = set()
        same = False
        dependency_length = len(self.dependencies)

        while not same:
            if closure_of == check_set:
                same = True
                break

            elif closure_of != check_set:
                check_set = closure_of.copy()
                for i in range(0, dependency_length):
                    if not same:
                        if self.contains(self.dependencies[i][0],closure_of):
                            closure_of.update(self.dependencies[i][1])

        return closure_of

    def key_from_closure(self, closure):
        pass

    # Every table used to be self.table, its changed now
    # https: // stackoverflow.com / questions / 27439192 / python - whats - the - difference - between -
    # set - difference - and -set - difference - update
    def decompose(self):

        # Create a copy of the attritbutes, in list format
        final_decomp = []
        done = False
        i = 0
        for attribute in [self.attributes]:
            final_decomp.append(attribute)

        while not done:
            if i == len(self.dependencies):
                done = True
                break

            for index in range(0,len(final_decomp)):
                difference = self.dependencies[i][1].symmetric_difference(self.dependencies[i][0])

                # Check to see that difference is a subset of the tables, so that no unwanted attributes are made
                if self.contains(difference, final_decomp[index]):
                    # Check that the two sets are not equal, ie: only one is a subset of the other
                    if difference is not final_decomp[index]:
                        final_decomp[index].difference_update(self.dependencies[i][1])
                        self.decomp_keys.append(self.dependencies[i][0])
                        final_decomp.append(difference)

            # Move onto the next element in the list
            i += 1

        self.all_tables = final_decomp
        return final_decomp


    def get_keys_decomp(self):
        return self.decomp_keys

    # Recursive implementation of the decompose function
    # Not entirely done yet
    def decomp(self, tables, dependency, max_len, index):
        if index < max_len:
            newset = dependency[1].symmetric_difference(dependency[0])
            if newset.issubset(list(tables[0])[index]) and newset != list(tables[0])[index]:
                list(tables[0])[index].difference_update(dependency[1])
                tables.append(list(tables[0])[index])

            index += 1
            return self.decomp(tables, dependency, max_len, index)

        else:
            return False

    # Try to implement a difference calculator between two sets
    # Just use built in .symmetric_difference().
    def get_difference(self, a, b):
        difference = list(set(a)-set(b))
        s = set(a)
        temp3 = [x for x in b if x not in s]
        return temp3

    # Find the key used to calculate a decomposition
    def find_key_for_decomp(self):
        keys = self.get_keys()
        tables = self.all_tables
        keys_final = []

        for key in keys:
            print(self.get_closure(key), key)
            closure_of_key = self.get_closure(key)
            if closure_of_key in tables:
                print(key)
            # for table in tables:
            #     print(set(key), table)
            #     if self.get_closure(set(key)) == list(table):

        return 0


    # Function to check for loss of dependency
    # Return of True indicates that dependency is lost
    def dependency_loss(self):
            # cont = True
            # index = 0
            # while cont:
            #     if index == len(self.dependencies):
            #         cont = False
            #         break
            #     # union_constant = self.union_constant(self.dependencies[index])
            #     if not self.union_constant(self.dependencies[index]):
            #         return True
            #     index += 1
            #
            # return False

        for dep in self.dependencies:
            if not self.union_constant(dep):
                return True
        return False

    def union_constant(self, dependency):

        pre = dependency[0].symmetric_difference(dependency[1])
        for attr_set in self.all_tables:
            if pre == attr_set:
                return True
        return False

        # for attributes in self.all_tables:
        #     if dependency[0].symmetric_difference(dependency[1]) == attributes:
        #         return True
        # return False

    # Get all possible combinations of the key
    # That way we can try smaller length strings before moving onto larger ones
    # remove-duplicates-in-list-of-lists-regardless-of-order-within-lists
    # Format must be {'a', 'b','c'} where a,b,c are candidate keys
    def formatted_combinations(self, dependencies, index):
        combination_list = []

        # Copy the original set, but pose it as a list
        duplicates_removed = list(dependencies)
        list_length = len(duplicates_removed) + 1

        # Create a combination of the elements
        # Make sure each element retrieved is only len index
        for L in range(0, list_length):
            for subset in itertools.combinations(duplicates_removed, index):
                combination_list.append(subset)

        # Remove duplicate pairings
        only_unique = {frozenset(x) for x in combination_list}

        return [list(x) for x in only_unique]