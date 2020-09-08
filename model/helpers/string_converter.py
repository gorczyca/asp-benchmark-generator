"""Provides helper functions for conversion between hierarchy expressed as string and Hierarchy object

The aforementioned string is in form where each '\n' character means another element and '\t' means child of the element
above.
"""

from typing import List, Tuple, Optional

from exceptions import BGError
from model.component import Component

CHILD_SYMBOL = '\t'
NEWLINE_SYMBOL = '\n'
NUMBER_OF_SPACES_EQUAL_TO_TAB = 4


def __extract_tabs(line: str) -> Tuple[int, str]:
    """Returns the component name and its level based on the number of \t symbols.

    :param line:    Line containing \t symbols and component's name.
    :return:       A tuple of the form (component's level, components'name).
    """
    tab_count = 0
    for letter in line:
        if letter != CHILD_SYMBOL:
            break
        else:
            tab_count += 1
    return tab_count, line.split()[0]


def string_to_hierarchy(hierarchy_string: str) -> List[Component]:
    """Converts string into Hierarchy object

    :param hierarchy_string:    hierarchy represented as string
    :return:   hierarchy's 'Hierarchy' object representation
    """
    hierarchy_string = hierarchy_string.replace(' ' * NUMBER_OF_SPACES_EQUAL_TO_TAB,
                                                CHILD_SYMBOL)  # make sure N spaces are converted to '\t'
    hierarchy = []
    last_on_level = []
    cmp_names = []

    for line in hierarchy_string.split('\n'):
        if not line or line.isspace():      # if entire line contains only spaces, ignore it
            continue
        level, component_name = __extract_tabs(line)
        if component_name in cmp_names:     # if names are not unique, raise error
            raise BGError(f'Hierarchy contains more than one component '
                          f'named "{component_name}".')
        else:
            cmp_names.append(component_name)
        if len(last_on_level) < level:      # if there are too many intendations,
            # raise error
            raise BGError(f'Cannot create a child of non-existing component. '
                          f'Check number of tabs in component: "{component_name} " '
                          f'and its ancestor.')
        component = Component(component_name, level)

        if len(last_on_level) > level:
            last_on_level[level] = component.id_  # there already exists a level
        else:
            last_on_level.append(component.id_)  # add level above
        if level != 0:
            component.parent_id = last_on_level[level - 1]

        hierarchy.append(component)
    return hierarchy


def hierarchy_to_string(hierarchy: List[Component]) -> str:
    """Converts 'Hierarchy' object to string.

    :param hierarchy:   'Hierarchy' object to be converted to string.
    :return:           Hierarchy's string representation.
    """
    def __hierarchy_to_string(hierarchy_: List[Component], string_: str, parent_id: Optional[int]) -> str:
        """Internal function used recursively.

        Appends the name of a child to current string and then calls itself looking for previously appended
        child's children.

        :param hierarchy_: Hierarchy list too look for components in.
        :param string_: Current string representation.
        :param parent_id:   Id of a parent component whose children (and then their children) are to be added to string.
        :return: String after adding component's children, and then their children recursively and so forth.
        """
        for cmp in hierarchy_:
            if cmp.parent_id == parent_id:
                string_ += cmp.level * CHILD_SYMBOL + cmp.name + NEWLINE_SYMBOL     # Add children string
                # Recursively add children of added children
                string_ = __hierarchy_to_string(hierarchy_, string_, cmp.id_)
        return string_
    return __hierarchy_to_string(hierarchy, '', None)
