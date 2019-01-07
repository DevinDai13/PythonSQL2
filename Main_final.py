import sqlite3
import re
from finalb import FunctionalDependencySet
from abc import ABC, abstractmethod

# This is the main file, all functions here relate to the program and are not methods
# https://stackoverflow.com/questions/7844118/how-to-convert-comma-delimited-string-to-list-in-python
# https://stackoverflow.com/questions/14856551/dynamic-triple-nested-list-in-python
# https://stackoverflow.com/questions/15102485/decomposing-a-relation-into-bcnf
# other sources will be located in their respective modules



def get_schema(c):
    c.execute("select Name "
              "from InputRelationSchemas")
    names = c.fetchall()

    # Create number for indexing and flatten the tuples
    print("All available schemas (selection is case sensitive):\n ")
    names = sum(names, ())
    number = 0

    for name in names:
        number += 1
        print("{number}. {name}"
              .format(number=number, name=name))

    return names


# Select the schema from user input and the list of available ones
# Implement error checking to see if input is valid
def select_schema(names):

    while True:
        schema_selected = input("Please select a schema to normalize")
        if schema_selected in names:
            print("The schema selected is available")
            print("")
            return schema_selected
        else:
            print("The schema selected does not exist")
            print("Please select one from: {names}"
                  .format(names=names))


# Get the foreign dependencies from the selected table
# Returns the foreign dependencies as a string
def get_dependencies(schema_selected, c):

    c.execute("select FDs from InputRelationSchemas "
              "where Name = '{schema}'"
              .format(schema=schema_selected))
    foreign_dependencies = c.fetchall()

    if foreign_dependencies:
        foreign_dependencies = str(foreign_dependencies[0][0])
        print("Foreign Dependencies: ")
        print(foreign_dependencies)
        print("")
        return foreign_dependencies
    else:
        print("There are no FDs")
        return 0


# Used to split the string into individual segments
def schema_reformat(foreign_dependencies):
    arrow_removed_dependencies = []
    braces_removed_dependencies = []

    split_dependencies = re.split(r";", foreign_dependencies)

    # This for loop is used to separate the arrows from the dependcy lists
    for dependency in split_dependencies:
        dependency = re.split(r"=>", dependency)
        arrow_removed_dependencies.append(dependency)

    # This for loop is used to remove whitespace and curly brackets
    for dependency_pair in arrow_removed_dependencies:
        for dependency in dependency_pair:
            new_str = dependency.replace("{", "")
            new_str = new_str.replace(" ", "")
            braces_removed_dependencies.append((new_str.replace("}", "")))

    # This for loop is used to group the list into groups of two
    composite_list = [braces_removed_dependencies[x:x + 2]
                      for x in range(0, len(braces_removed_dependencies), 2)]

    # b = []
    # print(composite_list)
    # for j in composite_list:
    #     for i in j:
    #         h = [x.strip() for x in i.split(',')]
    #         h = [h]
    #         b.append(h)

    b = []
    for j in composite_list:
        for i in j:
            h = [x.strip() for x in i.split(',')]
            b.append(h)

    c = [b[x:x + 2] for x in range(0, len(b), 2)]

    return c


# Get the required attributes for a schema
def get_attributes(c, schema):
    c.execute("select Attributes "
              "from InputRelationSchemas "
              "where Name = '{name}'"
              .format(name=schema))
    attributes = c.fetchall()

    ac = attributes[0][0]

    av = ac.split(",")
    g = []
    for i in av:
        g.append([i])

    if ac:
        print("Attributes: ")
        print(ac)
        print('')
        return g

    else:
        print("No Attributes")
        return 0
######################################


def get_f1_fd(c):
    table_name = input('Please enter table name: ')
    c.execute("select FDs from {table};".format(table=table_name))
    alist = c.fetchall()
    num = 0
    for item in alist:
        print(str(num + 1) + str(list(item)))
        num += 1
    fd_list = []
    while True:
        try:
            selected_fd = int(input('Please enter F1 FD choice (numbers 1,2,3...(or 0 to finish)): '))
        except ValueError:
            print("Not a number! Try again.")
            continue

        if selected_fd == 0:
            break
        fd1 = list(alist[int(selected_fd)-1])
        fd_list.append(fd1)

    result_list1 = []
    for i in range(len(fd_list)):
        broken_down = schema_decomposition(fd_list[i][0])
        for single_fd in broken_down:
            result_list1.append(single_fd)
    print('The selected F1 is {}'.format(result_list1))

    return result_list1


def get_f2_fd(c):
    table_name = input('Please enter table name: ')
    c.execute("select FDs from {table};".format(table=table_name))
    alist = c.fetchall()
    num = 0
    for item in alist:
        print(str(num+1) + str(list(item)))
        num += 1
    fd_list = []
    while True:
        try:
            selected_fd = int(input('Please enter F2 FD choice (numbers 1,2,3...(or 0 to finish)): '))
        except ValueError:
            print("Not a number! Try again.")
            continue

        if selected_fd == 0:
            break

        fd1 = list(alist[int(selected_fd)-1])
        fd_list.append(fd1)


    result_list2 = []
    for i in range(len(fd_list)):
        broken_down = schema_decomposition(fd_list[i][0])
        for single_fd in broken_down:
            result_list2.append(single_fd)
        print('The selected F2 is {}'.format(result_list2))

    return result_list2

def fd1infd2(fd1_set, fd2_set):
    fd_holds = []
    for i in range(len(fd1_set)):
        if fd1_set[i] in fd2_set:
            fd_holds.append(list(fd1_set[i]))
        else:
            closure_in_f2 = get_closure(fd1_set[i][0], fd2_set)
            closure_in_f1 = get_closure(fd1_set[i][0], fd1_set)
            if closure_in_f2 == closure_in_f1:
                fd_holds.append(list(fd1_set[i]))
            else:
                continue
    if fd_holds == fd1_set:
        return True
    else:
        return False

def fd2infd1(fd1_set, fd2_set):
    fd_holds = []
    for i in range(len(fd2_set)):
        if fd2_set[i] in fd1_set:
            fd_holds.append(list(fd2_set[i]))
        else:
            closure_in_f1 = get_closure(fd2_set[i][0], fd1_set)
            closure_in_f2 = get_closure(fd2_set[i][0], fd2_set)
            if closure_in_f1 == closure_in_f2:
                fd_holds.append(list(fd2_set[i]))
            else:
                continue
    if fd_holds == fd2_set:
        return True
    else:
        return False


def check_equal_fd(f1inf2, f2inf1):
    if f1inf2 and f2inf1 is True:
        print('The selected F1 and F2 are equivalent.')
    else:
        print('The selected F1 and F2 are not equivalent.')

#############################################  ATTRIBUTE CLOSURE FUNCTIONS ############################################
def schema_decomposition(foreign_dependencies):
    split_dependencies = re.split(r";", foreign_dependencies)

    arrow_removed_dependencies = []

    # This for loop is used to separate the arrows from the dependcy lists
    for dependency in split_dependencies:
        dependency = re.split(r"=>", dependency)
        arrow_removed_dependencies.append(dependency)

    braces_removed_dependencies = []

    # This for loop is used to remove whitespace and curly brackets
    for dependency_pair in arrow_removed_dependencies:
        for dependency in dependency_pair:
            new_str = dependency.replace("{", "")
            new_str = new_str.replace(" ", "")
            braces_removed_dependencies.append((new_str.replace("}", "")))

    # This for loop is used to group the list into groups of two
    composite_list = [braces_removed_dependencies[x:x + 2]
                      for x in range(0, len(braces_removed_dependencies), 2)]
    #print(composite_list)

    return composite_list

def closure_attribute_input():
    attributes = input('Please enter the attribute set: ')
    attribute_list = [str(x) for x in attributes.split(',')]
    print('The attribute set is {}'.format(attribute_list))
    return attribute_list

def closure_fd_input(c):
    table_name = input('Please enter table name: ')
    c.execute("select FDs from {};".format(table_name))
    alist = c.fetchall()
    num = 0
    for item in alist:
        print(str(num + 1) + str(list(item)))
        num += 1

    fd_list = []
    while True:
        try:
            selected_fd = int(input('Please enter FD choice (numbers 1,2,3...(or 0 to finish)): '))
        except ValueError:
            print("Not a number! Try again.")
            continue

        if selected_fd == 0:
            break

        fd1 = list(alist[int(selected_fd)-1])
        fd_list.append(fd1)


    result_list = []
    for i in range(len(fd_list)):
        broken_down = schema_decomposition(fd_list[i][0])
        for single_fd in broken_down:
            result_list.append(single_fd)

    print('The full FD set is {}'.format(result_list))

    return result_list

def closure_for_this_attribute():
    desired_attribute = input('Please enter the attribute you want to find the closure for (eg. A,B,C): ')
    return desired_attribute


def get_closure(attribute,f_set):
    closure_list = []
    temp_list = []
    B = []
    if len(attribute) >= 2:
        closure_list = list(attribute)
        closure_list = [x for x in closure_list if "," not in x]
        closure_list.append(attribute)
    else:
        closure_list.append(attribute)

    different = True
    while different:
        different = False
        for i in range(len(f_set)):
            if len(f_set[i][0]) == 1:
                if f_set[i][0] in closure_list:
                    if len(f_set[i][1]) > 1:
                        B = list(f_set[i][1])
                        B = [x for x in B if "," not in x]
                        B.append(f_set[i][1])
                    else:
                        B = [f_set[i][1]]
                    temp_list = set(closure_list)
                    closure_list = list(set().union(closure_list, B))
                    if set(temp_list) != set(closure_list):
                        different = True

            if len(f_set[i][0]) > 1:
                fd_left = list(f_set[i][0])
                fd_left = [x for x in fd_left if "," not in x]
                if (all(x in closure_list for x in fd_left)) is True:
                    if len(f_set[i][1]) > 1:
                        B = list(f_set[i][1])
                        B = [x for x in B if "," not in x]
                        B.append(f_set[i][1])
                    else:
                        B = [f_set[i][1]]
                    temp_list = set(closure_list)
                    closure_list = list(set().union(closure_list, B))
                    if set(temp_list) != set(closure_list):
                        different = True


    closure_list = [x for x in closure_list if not len(x) > 1]

    return sorted(closure_list)

def print_closure(closure):
    return print('The closure is: {}'.format(sorted(closure)))

######################################

# Ask the user to provide a db file, if it doesnt exists, the system will create one, except handles other errors
def main():
    print("Welcome to the program")
    while True:
        try:
            print('\n')
            conn = db_connect()
            option = main_menu(conn.cursor(), conn)
            conn.commit()
            conn.close()

        except TypeError:
            print("Please enter a valid file name")
            print("Exiting program")

        else:
            if option == 'quit':
                break

    return 0


def main_menu(cursor, conn):
    print('Please select an option for the program to perform (by number): ')
    print('1. Get the BCNF of a dependency')
    print('2. Get closure')
    print('3. Check equal FD')
    print('Enter quit to terminate Program')
    selection = input(' ')
    tasks(selection, cursor, conn)

    return selection

# Function to process user input and complete a task accordingly
def tasks(task, cursor, conn):
    if task == 'quit':
        print('Program terminated.')
        return 0

    elif int(task) == 1:
        BCNF_tasks(cursor, conn)

    elif int(task) == 2:
        closure_attribute_input()
        f_dependency = closure_fd_input(cursor)
        attribute = closure_for_this_attribute()
        closure = get_closure(attribute, f_dependency)
        print_closure(closure)


    elif int(task) == 3:
        fd_1 = get_f1_fd(cursor)
        fd_2 = get_f2_fd(cursor)
        res1 = fd1infd2(fd_1, fd_2)
        res2 = fd2infd1(fd_1, fd_2)
        check_equal_fd(res1, res2)

    else:
        print("Invalid input")


def BCNF_tasks(cursor, conn):
    names = get_schema(cursor)
    schema_name = select_schema(names)
    # schema_name = "R1"
    dependencies = get_dependencies(schema_name, cursor)
    if dependencies != 0:
        dependency_list = schema_reformat(dependencies)
        attributes = get_attributes(cursor, schema_name)
        if attributes != 0:
            print("So far so good")
            print('')

            gg = FunctionalDependencySet(attributes, schema_name)
            add_dependencies(gg, dependency_list)

            print("Keys provided:")
            print(gg.get_keys())
            print('')

            print("Candidate (minimal) key(s) computed (May include those provided):")
            candidate_keys = gg.find_candidate_keys()
            print(candidate_keys)
            print('')

            print("All Keys Retrieved (Includes those provided and computed by the algorithm): ")
            print(gg.get_keys())
            print('')

            print("Decomposition: ")
            decomp = gg.decompose()
            v = []
            for j in decomp:
                if j != set():
                    v.append(j)
            print(v)
            print('')

            store_output(cursor, gg, v, candidate_keys)
            create_tables(cursor, gg)
            conn.commit()

        else:
            print("No dependencies available")
    else:
        return 0

    return 0

def store_output(cursor, gg, decomp,candidate_keys):
    name = str(gg.get_name())
    decomp_sorted = list(map(sorted, decomp))
    # print(list(decomp_sorted))

    # Format the names of the table instances
    format_names = []
    for i in decomp_sorted:
        j = '_'.join(i)
        h = name + '_' + j
        format_names.append(h)

    # Format the attributes to be inserted
    format_attr = []
    for i in decomp_sorted:
        j = ','.join(i)
        format_attr.append(j)

    f = list(gg.get_keys_decomp())
    format_fds = f.copy()

    for i in range(0, len(candidate_keys)):
        format_fds.insert(i,candidate_keys[0])

    # Get the RHS of the equation
    format_fds_RHS = []

    for index in range(0, len(decomp)):
        if decomp[index] != format_fds[index]:
            format_fds_RHS.append(decomp[index] - format_fds[index])
        else:
            format_fds_RHS.append(decomp[index])

    for i in format_fds_RHS:
        list(i).sort()

    reformated_fds = []
    for index in range(0, len(decomp)):
        j = sorted(list(format_fds[index]))
        j = ", ".join(j)
        l = sorted(list(format_fds_RHS[index]))
        l = ", ".join(l)
        f = '{' + str(j) + '}' + " => " + '{' + str(l) + '}'
        reformated_fds.append(f)

    cursor.execute("Delete from OutputRelationSchemas")

    for index in range(len(format_names)-1, -1, -1):
        cursor.execute("Insert into OutputRelationSchemas "
                  "values (?,?,?) "
                  ,(format_names[index], format_attr[index],
                    reformated_fds[index]))

    loss = gg.dependency_loss()

    if loss:
        print("The decomposition is not dependency conserving")
    else:
        print("The decomposition is dependency conserving")

    return 0


def add_dependencies(gg, dependency_list):
    for i in dependency_list:
        gg.add_dependency(i)

    return 0


def create_tables(cursor, gg):
    cursor.execute("Select Name from OutputRelationSchemas "
                   "where Name LIKE '{name}_%'".format(name=gg.get_name()))

    f = cursor.fetchall()
    cursor.execute("PRAGMA table_info({name});".format(name=gg.get_name()))
    j = cursor.fetchall()
    print("The following information of the table:")
    print(j)
    print('')

    for j in f:
        types = []
        print("Creating Table {}".format(j[0]))
        cursor.execute("Select Attributes from OutputRelationSchemas "
                  "where Name = '{name}'".format(name=j[0]))
        b = cursor.fetchall()[0]
        for bb in b:
            if bb != '':
                for bbb in b:
                    print("With attributes " + bbb)
                    print('')

        # cursor.execute(" CREATE TABLE IF NOT EXISTS {name} ("
        #                 "{id} {integer PRIMARY KEY);")




# Function to connect to the database
def db_connect():
    sqlite_file = input("Please enter the name of the Database: ")
    #sqlite_file = "a.sqliteDB"
    conn = sqlite3.connect(str(sqlite_file))
    print("{} has been successfully connected to ".format(sqlite_file))
    print("")
    return conn


# Unit tests, kinda
def Unit_test():
    sqlite_file = input('Please enter database: ')
    conn = sqlite3.connect(str(sqlite_file))
    print("{} has been successfully connected to ".format(sqlite_file))
    print("")
    BCNF_tasks(conn.cursor(), conn)
    conn.commit()
    conn.close()

    # bar = FunctionalDependencySet([['A'], ['B'], ['C'], ['D'], ['E'], ['F'], ['G']], 'bepis')
    # bar.add_dependency([['A', 'B'], ['C', 'D']])
    # bar.add_dependency([['C'], ['E', 'F']])
    # bar.add_dependency([['G'], ['A']])
    # bar.add_dependency([['G'], ['F']])
    # bar.add_dependency([['C', 'E'], ['F']])
    # print(bar.find_candidate_keys())
    # print(bar.dependency_loss())
    #
    # baz = FunctionalDependencySet([['A'],['N'],['B'],['G'],['P']], 'ok')
    # baz.add_dependency([['A'], ['N']])
    # baz.add_dependency([['B'], ['G','P']])
    # print(baz.decompose())
    # print(baz.dependency_loss())
    #
    # wuz = FunctionalDependencySet([['A'],['B'],['C']], 'j')
    # wuz.add_dependency([['A','B'], ['C']])
    # wuz.add_dependency([['C'], ['A']])
    # print(wuz.decompose())
    # print(wuz.dependency_loss())


main()