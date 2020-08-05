from typing import List, Optional, Tuple, Any
import json

from exceptions import BGError
from model.complex_constraint import ComplexConstraint
from model.component import Component
from model.resource import Resource
from model.port import Port
from model.simple_constraint import SimpleConstraint

SPACE_REPLACEMENT = '_'


class Model:
    """Serves the communication between View and Controller.

    Gathers in one place all configuration's problem instance information.

    Attributes:
        hierarchy:  Hierarchy of components. Hierarchy of components is naturally a tree structure. Because of 
        complexity issues (to avoid recursion) it is implemented as a List with component having a pointer to its 
        ancestor. Still, recursion could not be completely avoided (e.g. when removing a component recursively or 
        creating a string from hierarchy)

        resources:  List of resources
        ports: List of ports
    """
    def __init__(self, root_name: str = None, hierarchy: List[Component] = None, resources: List[Resource] = None, ports: List[Port] = None,
                 simple_constraints: List[SimpleConstraint] = None, complex_constraints: List[ComplexConstraint] = None):
        self.root_name: str = root_name
        self.hierarchy: List[Component] = hierarchy if hierarchy is not None else []
        self.resources: List[Resource] = resources if resources is not None else []
        self.ports: List[Port] = ports if ports is not None else []
        self.simple_constraints: List[SimpleConstraint] = simple_constraints if simple_constraints is not None else []
        self.complex_constraints: List[ComplexConstraint] = complex_constraints if complex_constraints is not None else []

    @staticmethod
    def replace_space(string: str):
        return string.replace(' ', SPACE_REPLACEMENT)

    def clear(self):
        """Clears out all Model's attributes and sets the new root name."""
        self.hierarchy = []
        self.resources = []
        self.ports = []
        self.simple_constraints = []
        self.complex_constraints = []

    @classmethod
    def from_json(cls, json_string):
        """Necessary to create an instance from JSON."""
        data = json.loads(json_string)
        data['hierarchy'] = list(map(Component.from_json, data['hierarchy']))
        data['resources'] = list(map(Resource.from_json, data['resources']))    # Convert dictionary to object
        data['ports'] = list(map(Port.from_json, data['ports']))
        data['simple_constraints'] = list(map(SimpleConstraint.from_json, data['simple_constraints']))
        data['complex_constraints'] = list(map(ComplexConstraint.from_json, data['complex_constraints']))
        return cls(**data)

    # def json_to_model(json_string: str) -> Model:
    #     """Converts the JSON string to the Hierarchy object"""
    #     return Model.from_json(json.loads(json_string))

    # Root component
    def set_root_name(self, root_name: str) -> None:
        cmps_names = [c.name for c in self.hierarchy]
        root_name = self.replace_space(root_name)
        if not root_name:
            raise BGError('Root component must have a name.')
        if root_name in cmps_names:
            raise BGError(f'Component with name: "{root_name}" already exists in the hierarchy.')
        self.root_name = root_name

    # Hierarchy
    def set_hierarchy(self, hierarchy: List[Component]):
        self.hierarchy = hierarchy
        self.__set_leaves()

    def __set_leaves(self) -> None:
        """Traverses through hierarchy and sets the property is_leaf of leaf components to True.

        Used when hierarchy is changed.
        """
        parents_ids = [cmp.parent_id for cmp in self.hierarchy if cmp.parent_id is not None]
        parents_ids = set(parents_ids)

        for cmp in self.hierarchy:
            if cmp.id_ not in parents_ids:
                # Cmp is a leaf
                cmp.is_leaf = True
                cmp.symmetry_breaking = True
            else:
                # Cmp is not a leaf
                cmp.is_leaf = False
                cmp.symmetry_breaking = None
                cmp.count = None
                cmp.produces = {}
                cmp.ports = {}

    def add_component_to_hierarchy(self, cmp_name: str, level: int, parent_id: Optional[int], is_leaf: bool = True) -> Component:
        """Creates and adds new component to hierarchy.

        :param cmp_name: Name.
        :param level: Level.
        :param parent_id: Id of parent.
        :param is_leaf: True if component is a leaf-component; False otherwise.
        :returns: Created component
        """
        if not cmp_name:
            raise BGError('Component must have a name.')
        cmp_name = self.replace_space(cmp_name)
        cmps_names = [c.name for c in self.hierarchy]
        if cmp_name in cmps_names:
            raise BGError(f'Component with name: "{cmp_name}" already exists in the hierarchy.')
        if cmp_name == self.root_name:
            raise BGError(f'Component cannot have same name as the root component.')
        symmetry_breaking = True if is_leaf else None
        cmp = Component(cmp_name, level, parent_id=parent_id, is_leaf=is_leaf,
                        symmetry_breaking=symmetry_breaking)
        self.hierarchy.append(cmp)
        self.__set_leaves()
        return cmp

    def remove_component_from_hierarchy_recursively(self, cmp: Component) -> List[Component]:
        """Removes the component recursively (the component itself, its children, the children of the children...).

        :param cmp: Component to remove.
        :returns: List of components removed from the hierarchy.
        """
        def __remove_component(cmp_: Component, hierarchy_: List[Component], to_remove_: List[Component]) -> None:
            """Creates a list of components to remove by recursive calls to itself.

            :param cmp_: Current component to remove (and all its children recursively).
            :param hierarchy_: Components hierarchy.
            :param to_remove_: List of components to be removed.
            """
            to_remove_.append(cmp_)     # Add current element to list of elements to remove.
            for c in hierarchy_:
                if c.parent_id == cmp_.id_:
                    __remove_component(c, hierarchy_, to_remove_)   # Recursively remove all the component's children

        to_remove = []
        __remove_component(cmp, self.hierarchy, to_remove)
        self.hierarchy = [cmp for cmp in self.hierarchy if cmp not in to_remove]
        self.__set_leaves()
        return to_remove

    def get_component_and_its_children(self, cmp: Component) -> List[Component]:
        def __get_component_and_children(cmp_: Component, hierarchy_: List[Component], children_: List[Component]) -> None:
            children_.append(cmp_)
            for c in hierarchy_:
                if c.parent_id == cmp_.id_:
                    __get_component_and_children(c, hierarchy_, children_)

        list_ = []
        __get_component_and_children(cmp, self.hierarchy, list_)
        return list_

    def remove_component_from_hierarchy_preserve_children(self, cmp: Component) -> None:
        """Removes the component from hierarchy, but preserves its children.

        The children of the removed component are placed on their ancestor's place; Their parent_id attribute is set
        to their actual parent's parent_id attribute.

        :param cmp: Component to remove.
        :returns: List of removed components children.
        """
        for c in self.hierarchy:
            if c.parent_id == cmp.id_:
                c.parent_id = cmp.parent_id
        self.hierarchy.remove(cmp)
        self.__set_leaves()

    def get_component_by_id(self, id_: int) -> Component:
        """Returns component, that has the specified id

        :param id_: Id of the parameter to return
        :returns: Component with the given id.
        """
        return next((cmp for cmp in self.hierarchy if cmp.id_ == id_), None)

    def get_components_by_ids(self, ids: List[int]) -> List[Component]:
        """Returns a list of components that have their ids among given ids list.

        :param ids: List of ids of components to return.
        :returns: List of components.
        """
        return [c for c in self.hierarchy if c.id_ in ids]

    def get_leaf_components(self) -> List[Component]:
        """Returns a list of component that are leaves.

        :returns: List of leaf-components
        """
        return [c for c in self.hierarchy if c.is_leaf]

    def rename_component(self, cmp: Component, new_name: str) -> Component:
        """Changes name of a specified component.

        Raises BGError when a component with the new name already exists in the hierarchy.
        :param cmp: Component
        :param new_name: New name for component
        :returns: Component with its name changed
        """
        if not new_name:
            raise BGError('Component must have a name')
        cmps_names = [c.name for c in self.hierarchy]
        if new_name in cmps_names:
            raise BGError(f'Component with name: "{new_name}" already exists in the hierarchy.')
        cmp.name = new_name
        return cmp

    def __get_components_leaf_children(self, cmp_: Component, hierarchy_: List[Component], leaves_: List[Component]):
        """Returns an array of Component children that are leaves (obtained recursively)

        :param cmp_: Current component to check whether is a leaf or not
        :param hierarchy_: Hierarchy of all components
        :param leaves_: Current list of leaves
        """
        # TODO: take this function out, to be able to get to component's children from anywhere
        if cmp_.is_leaf:
            leaves_.append(cmp_)
        else:
            for c_ in hierarchy_:
                if c_.parent_id == cmp_.id_:
                    self.__get_components_leaf_children(c_, hierarchy_, leaves_)

    # Instances
    def set_instances_of_all_components_children(self, cmp: Component, count: int, symmetry_breaking: bool) -> List[Component]:
        """
        :param cmp:
        :param count:
        :param symmetry_breaking:
        :return:
        """
        def __get_components_leaf_children(cmp_: Component, hierarchy_: List[Component], leaves_: List[Component]):
            # TODO: remove!!!
            """Returns an array of Component children that are leaves (obtained recursively)

            :param cmp_: Current component to check whether is a leaf or not
            :param hierarchy_: Hierarchy of all components
            :param leaves_: Current list of leaves
            """
            # TODO: take this function out, to be able to get to component's children from anywhere
            if cmp_.is_leaf:
                leaves_.append(cmp_)
            else:
                for c_ in hierarchy_:
                    if c_.parent_id == cmp_.id_:
                        __get_components_leaf_children(c_, hierarchy_, leaves_)

        leaf_children = []
        self.__get_components_leaf_children(cmp, self.hierarchy, leaf_children)
        for c in leaf_children:
            c.count = count
            c.symmetry_breaking = symmetry_breaking
        return leaf_children

    # Resources
    def get_all_resources_names(self) -> List[str]:
        """Returns a list with all resources names."""
        return [r.name for r in self.resources]

    def add_resource(self, name: str) -> Resource:
        """Creates a resource with a specified name. Raises ResourceError whenever such  resource already exists

        :param name: Name of the resource
        :returns: Created Resource.
        """
        resources_names = self.get_all_resources_names()
        if name in resources_names:
            raise BGError(f'Resource "{name}" already exists.')
        resource = Resource(name)
        self.resources.append(resource)
        return resource

    def get_resource_by_name(self, name: str) -> Resource:
        """Returns resource, that has the specified name

        :param name: Name of the resource
        :returns: Port with the specified name.
        """
        return next((res for res in self.resources if res.name == name), None)

    def get_resource_by_id(self, id_: int) -> Resource:
        """TODO:

        """
        return next((res for res in self.resources if res.id_ == id_), None)

    def change_resource_name(self, res: Resource, new_name: str) -> Resource:
        """Changes name of a specified resource.

        Raises ResourceStringError when a resource with the new name already exists.
        :param res: Resource
        :param new_name: New name for resource
        :returns: Resource with its name changed
        """
        res_names = self.get_all_resources_names()
        if new_name in res_names:
            raise BGError(f'Resource with name: "{new_name}" already exists in the hierarchy.')
        res.name = new_name
        return res

    def remove_resource(self, res: Resource) -> Resource:
        """Removes resource from model and all the references to it by its id in Component.produces.

        :param res: Resource to be removed from model.
        :returns: Removed Resource.
        """
        for c in self.hierarchy:
            if res.id_ in c.produces:
                del c.produces[res.id_]     # Remove information about production of this resource from components

        self.resources.remove(res)  # Remove component itself
        return res

    def __get_components_children(self, cmp_: Component, hierarchy_: List[Component], children_: List[Component]):
        """Returns an array of Component children (obtained recursively)

        :param cmp_: Current component
        :param hierarchy_: Hierarchy of all components
        :param children_: Current list of children
        """
        # TODO: take this function out, to be able to get to component's children from anywhere
        # TODO: its only leaves
        if cmp_.is_leaf:
            children_.append(cmp_)
        else:
            for c_ in hierarchy_:
                if c_.parent_id == cmp_.id_:
                    self.__get_components_children(c_, hierarchy_, children_)

    def set_ports_amount_to_all_components_children(self, cmp: Component, prt: Port, value: int) \
            -> List[Component]:
        children = []
        self.__get_components_children(cmp, self.hierarchy, children)
        leaf_children = [c for c in children if c.is_leaf]
        for c in leaf_children:
            c.ports[prt.id_] = value
        return leaf_children

    def set_resource_production_to_all_components_children(self, cmp: Component, res: Resource, value: int) \
            -> List[Component]:
        """Sets the production of a resource to specific value for all leaf-component children.

        :param cmp: Component to set the children production of.
        :param res: Production of this Resource
        :param value: Amount of produced Resource by components
        :returns: List of Component's children that are leaves.
        """
        # TODO: remove
        # def __get_components_leaf_children(cmp_: Component, hierarchy_: List[Component], leaves_: List[Component]):
        #     """Returns an array of Component children that are leaves (obtained recursively)
        #
        #     :param cmp_: Current component to check whether is a leaf or not
        #     :param hierarchy_: Hierarchy of all components
        #     :param leaves_: Current list of leaves
        #     """
        #     if cmp_.is_leaf:
        #         leaves_.append(cmp_)
        #     else:
        #         for c_ in hierarchy_:
        #             if c_.parent_id == cmp_.id_:
        #                 __get_components_leaf_children(c_, hierarchy_, leaves_)

        leaf_children = []
        self.__get_components_leaf_children(cmp, self.hierarchy, leaf_children)
        for c in leaf_children:
            c.produces[res.id_] = value
        return leaf_children

    # Port
    def add_port(self, name: str) -> Tuple[Port, int]:
        """Creates a port with a specified name. Raises PortError whenever such resource already exists

        :param name: Name of the Port
        :returns: tuple (Created Port, index of created port in the list of ports sorted alphabetically)
        """
        # TODO: remove index
        port_names = [p.name for p in self.ports]
        if name in port_names:
            raise BGError(f'Port "{name}" already exists.')
        port = Port(name)
        self.ports.append(port)
        port_names_sorted = sorted([p.name for p in self.ports])
        index = port_names_sorted.index(name)
        # TODO: remove returning index
        return port, index

    def change_port_name(self, prt: Port, new_name: str) -> Tuple[Port, int]:
        """Changes name of a specified port.

        Raises PortError when a port with the new name already exists.
        :param prt: Port
        :param new_name: New name for port
        :returns: tuple (Port, index of port with the name edited)
        """
        port_names = [p.name for p in self.ports]
        if new_name in port_names:
            raise BGError(f'Port "{new_name}" already exists.')
        prt.name = new_name
        # TODO: do it better, sort the ports list and then take port
        port_names_sorted = sorted([p.name for p in self.ports])
        index = port_names_sorted.index(new_name)
        # TODO: do not remove index
        return prt, index

    def get_port_by_id(self, id_: int) -> Port:
        """Returns port, that has the specified id

        :param id_: Id of the Port to return
        :returns: Port with the given id.
        """
        return next((prt for prt in self.ports if prt.id_ == id_), None)

    def get_port_by_name(self, name: str) -> Port:
        """Returns port, that has the specified name

        :param name: Name of the port
        :returns: Port with the specified name.
        """
        return next((prt for prt in self.ports if prt.name == name), None)

    def get_ports_by_ids(self, ids: List[int]) -> List[Port]:
        return [p for p in self.ports if p.id_ in ids]

    def remove_port(self, prt: Port) -> Port:
        """Removes port from model and all the references to it by its id in Component.ports.

        :param prt: Port to be removed from model.
        :returns: Removed Port.
        """
        for c in self.hierarchy:
            if prt.id_ in c.ports:
                del c.ports[prt.id_]     # Remove information about ports from components

        self.ports.remove(prt)  # Remove port itself
        return prt

    def get_all_ports_names(self) -> List[str]:
        """Returns a list with all ports names."""
        return [p.name for p in self.ports]

    def update_ports_compatibility(self, port, compatible_ports) -> None:
        compatible_ports_ids = [p.id_ for p in compatible_ports]
        # If compatibility was removed
        ports_to_remove_ids = [pid for pid in port.compatible_with if pid not in compatible_ports_ids]
        # Remove from the other ports the compatibility with this port
        for pid in ports_to_remove_ids:
            port_ = self.get_port_by_id(pid)
            port_.compatible_with.remove(port.id_)
        # Add to other ports compatibility with this port
        for pid in compatible_ports_ids:
            port_ = self.get_port_by_id(pid)
            if port.id_ not in port_.compatible_with:
                port_.compatible_with.append(port.id_)
        port.compatible_with = compatible_ports_ids

    # Constraint (Simple & Complex)
    def get_all_constraints(self) -> List[Any]:
        """Returns a union of sets of simple & complex constraints.

        :returns: Set of simple & complex constraints
        """
        return [*self.simple_constraints, *self.complex_constraints]

    def get_constraint_by_id(self, id_: int):
        """Returns a constraint by a given id. Note: 'Constraint' might be an instance of either SimpleConstraint or ComplexConstraint

        :param id_: Id of the constraint to return.
        :returns: SimpleConstraint or ComplexConstraint instance with a given id
        """
        simple_ctr = next((c for c in self.simple_constraints if c.id_ == id_), None)
        # Look in the simple constraints first
        return simple_ctr if simple_ctr is not None \
            else next((c for c in self.complex_constraints if c.id_ == id_), None)  # Then look in the complex ones

    def add_constraint(self, ctr: Any) -> Tuple[Any, int]:
        """Adds constraint to the model (either to the list of simple constraints or complex).

        :param ctr: Constraint to add to the model
        :returns: Added constraint and index of it in the sorted alphabetically union of simple
        and complex constraints (Simple constraints are put first in the union, complex constraints later).
        """
        if not ctr.name:
            raise BGError('Constraint must have a name.')
        ctr_names = [*[s.name for s in self.simple_constraints], *[c.name for c in self.complex_constraints]]
        if ctr.name in ctr_names:
            raise BGError(f'Constraint with the name {ctr.name} already exists.')

        if isinstance(ctr, SimpleConstraint):
            # TODO: already insert in sorted maybe?
            self.simple_constraints.append(ctr)
        else:
            self.complex_constraints.append(ctr)
        sorted_ctrs_names = [*sorted([s.name for s in self.simple_constraints]), *sorted([c.name for c in self.complex_constraints])]
        return ctr, sorted_ctrs_names.index(ctr.name)

    def remove_constraint(self, ctr: Any) -> Any:
        """Removes constraint from the model (either from the list of simple constraints or complex).

        :param ctr: Constraint to remove from the model.
        :returns: Removed constraint
        """
        if isinstance(ctr, SimpleConstraint):
            self.simple_constraints.remove(ctr)
        else:
            self.complex_constraints.remove(ctr)
        return ctr

    def get_constraint_index(self, ctr: Any):
        sorted_ctrs_names = [*sorted([p.name for p in self.simple_constraints]), *sorted([p.name for p in self.complex_constraints])]
        return sorted_ctrs_names.index(ctr.name)

