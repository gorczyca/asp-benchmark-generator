from typing import List, Tuple, Any
import json

from json_converter import deserialize_list
from model.helpers import normalize_name, matches
from exceptions import BGError

from model.simple_constraint import SimpleConstraint
from model.component import Component
from model.complex_constraint import ComplexConstraint
from model.port import Port
from model.resource import Resource


class Model:
    """Gathers in one place all configuration's problem instance information.

    Attributes:
        root_name: Name of the root component.
        taxonomy:  Taxonomy of components - tree structure, implemented as a list of components,
            each of them having a pointer to the parent component (or None if there is no parent).
        resources:  List of resources.
        ports: List of ports.
        simple_constraints: List of simple constraints.
        complex_constraints: List of complex constraints.
    """
    def __init__(self,
                 root_name: str = None,
                 taxonomy: List[Component] = None,
                 resources: List[Resource] = None,
                 ports: List[Port] = None,
                 simple_constraints: List[SimpleConstraint] = None,
                 complex_constraints: List[ComplexConstraint] = None):
        self.root_name: str = root_name
        self.taxonomy: List[Component] = taxonomy if taxonomy is not None else []
        self.resources: List[Resource] = resources if resources is not None else []
        self.ports: List[Port] = ports if ports is not None else []
        self.simple_constraints: List[SimpleConstraint] = simple_constraints if simple_constraints is not None else []
        self.complex_constraints: List[ComplexConstraint] = complex_constraints if complex_constraints is not None else []

    def clear(self):
        """Clears out all Model's attributes and sets the new root name."""
        self.taxonomy.clear()
        self.resources.clear()
        self.ports.clear()
        self.simple_constraints.clear()
        self.complex_constraints.clear()

    @classmethod
    def from_json(cls, json_string):
        """Necessary to create an instance from JSON."""
        data = json.loads(json_string)
        data['taxonomy'] = deserialize_list(Component, data['taxonomy'])
        data['resources'] = deserialize_list(Resource, data['resources'])  # Convert dictionary to object
        data['ports'] = deserialize_list(Port, data['ports'])
        data['simple_constraints'] = deserialize_list(SimpleConstraint, data['simple_constraints'])
        data['complex_constraints'] = deserialize_list(ComplexConstraint, data['complex_constraints'])
        return cls(**data)

    # Root component
    def set_root_name(self, root_name: str) -> None:
        """Sets the name of the root component.

        :param root_name: Name of the root component.
        """
        root_name = normalize_name(root_name)
        if root_name in self.get_all_components_names():
            raise BGError(f'Component with name: "{root_name}" already exists in the taxonomy.')
        self.root_name = root_name

    # Taxonomy
    def set_taxonomy(self, taxonomy: List[Component]) -> None:
        """Sets the model component's taxonomy. Then updates each component's information.

        :param taxonomy: List of components representing the taxonomy.
        """
        self.taxonomy = taxonomy
        self.__update_taxonomy()

    def __update_taxonomy(self) -> None:
        """Traverses through taxonomy and sets the default properties of "leaf" and "non-leaf" components.
        Used when taxonomy is changed.
        """
        parents_ids = [cmp.parent_id for cmp in self.taxonomy if cmp.parent_id is not None]
        parents_ids = set(parents_ids)

        for cmp in self.taxonomy:
            if cmp.id_ not in parents_ids:
                # Cmp is a leaf
                cmp.is_leaf = True
                cmp.symmetry_breaking = True
            else:
                # Cmp is not a leaf
                cmp.is_leaf = False
                cmp.symmetry_breaking = None
                cmp.count = None
                cmp.min_count = None
                cmp.max_count = None
                cmp.produces = {}
                cmp.ports = {}

    def add_component(self, cmp: Component) -> Component:
        """Creates and adds new component to taxonomy.

        :param cmp: Component to add to taxonomy.
        :return: Added component.
        """
        cmp.name = normalize_name(cmp.name)
        if cmp.name in self.get_all_components_names():
            raise BGError(f'Component with name: "{cmp.name}" already exists in the taxonomy.')
        elif cmp.name == self.root_name:
            raise BGError(f'Component cannot have same name as the root component.')
        self.taxonomy.append(cmp)
        self.__update_taxonomy()
        return cmp

    def remove_component_recursively(self, cmp: Component) -> Tuple[List[Component], List[Any]]:
        """Removes the component recursively (the component itself, its children, the children's children etc.).

        :param cmp: Component to remove.
        :return: Tuple of the form (list of components removed from the taxonomy,
                                    list of constraints removed from model [because of removing of the component])
        """
        cmp_children = self.get_components_children(cmp)
        cmps_to_remove = [cmp, *cmp_children]
        self.taxonomy = [cmp for cmp in self.taxonomy if cmp not in cmps_to_remove]
        self.__update_taxonomy()
        removed_ctrs = [ctr for cmp in cmps_to_remove for ctr in self.__remove_components_constraints(cmp)]
        return cmps_to_remove, removed_ctrs

    def __remove_components_constraints(self, cmp: Component) -> List[Any]:
        """Removes component from model. Looks for references of the removed component in the constraints
        and removes this constraints from the model as well.

        :param cmp: Component to remove.
        :return: List of constraints removed that contained component.
        """
        simple_ctr_to_remove = []
        for sc in self.simple_constraints:
            if cmp.id_ in sc.components_ids:
                simple_ctr_to_remove.append(sc)

        complex_ctr_to_remove = []
        for cc in self.complex_constraints:
            for ctr in [*cc.antecedent, *cc.consequent]:
                if cmp.id_ in ctr.components_ids:
                    complex_ctr_to_remove.append(cc)
                    break

        # Remove simple constraints
        self.simple_constraints = [sc for sc in self.simple_constraints if sc not in simple_ctr_to_remove]
        # Remove complex constraints
        self.complex_constraints = [cc for cc in self.complex_constraints if cc not in complex_ctr_to_remove]
        return simple_ctr_to_remove + complex_ctr_to_remove

    def get_components_children(self, cmp: Component, **kwargs) -> List[Component]:
        """Returns the list of component's children (obtained recursively).

        :param cmp: Component, to return the children of.
        :param kwargs: Additional parameters of the desired children components.
        :return: List of component's children.
        """
        def __get_components_children(cmp_: Component, children_: List[Component]) -> None:
            """Creates a list of children of the cmp_ component, be recursive calls to itself.

            :param cmp_: Component, to create the children's list of.
            :param children_: List of child components.
            """
            for c in self.taxonomy:
                if c.parent_id == cmp_.id_:
                    if matches(c, **kwargs):
                        children_.append(c)
                    __get_components_children(c, children_)

        children = []
        __get_components_children(cmp, children)
        return children

    def remove_component_preserve_children(self, cmp: Component) -> Tuple[Component, List[Any]]:
        """Removes the component from taxonomy, but preserves its children.

        The children of the removed component are placed on their ancestor's place; Their parent_id attribute is set
        to their actual parent's parent_id attribute.

        :param cmp: Component to remove.
        :return: Tuple of the form (component removed from the taxonomy,
                                    list of constraints removed from model [because of removing of the component])
        """
        for c in self.taxonomy:
            if c.parent_id == cmp.id_:
                c.parent_id = cmp.parent_id
        self.taxonomy.remove(cmp)
        self.__update_taxonomy()
        return cmp, self.__remove_components_constraints(cmp)

    def get_component(self, **kwargs) -> Component:
        """Returns the first component whose attributes match the kwargs.

        :param kwargs: Desired attributes of a component.
        :return: Component.
        """
        return next((cmp for cmp in self.taxonomy if matches(cmp, **kwargs)), None)

    def get_components(self, **kwargs) -> List[Component]:
        """Returns a list of components with attributes that match the kwargs.

        :param kwargs: Desired attributes of a components.
        :return: List of components.
        """
        return [c for c in self.taxonomy if matches(c, **kwargs)]

    def get_components_by_ids(self, ids: List[int]) -> List[Component]:
        """Returns a list of components that have their ids among given ids list.

        :param ids: List of ids of components to return.
        :return: List of components.
        """
        return [c for c in self.taxonomy if c.id_ in ids]

    def rename_component(self, cmp: Component, new_name: str) -> Component:
        """Changes name of a specified component.

        :param cmp: Component
        :param new_name: New name for component
        :return: Component with its name changed
        """
        new_name = normalize_name(new_name)
        if new_name in self.get_all_components_names() and cmp.name != new_name:    # Allow changing name for the same
            raise BGError(f'Component with name: "{new_name}" already exists in the taxonomy.')
        cmp.name = new_name
        return cmp

    def get_all_components_names(self):
        """Returns a list of all components names.

        :return: List of all components names.
        """
        return [c.name for c in self.taxonomy]

    def set_components_leaf_children_properties(self, cmp: Component, **kwargs):
        """Sets the attributes of the leaf children of cmp to those specified in kwargs.

        :param cmp: Component whose leaf children attributes are to be changed.
        :param kwargs: Attributes and their values to set.
        :return: Leaf children with their attributes changed.
        """
        leaf_children = self.get_components_children(cmp, is_leaf=True)
        for c in leaf_children:
            for attr, val in kwargs.items():
                setattr(c, attr, val)
        return leaf_children

    def set_all_leaf_components_properties(self, **kwargs):
        """Sets the attributes of all leaf components to those specified in kwargs.

        :param kwargs: Attributes and their values to set.
        :return: Leaf children with their attributes changed.
        """
        leaf_cmps = self.get_components(is_leaf=True)
        for c in leaf_cmps:
            for attr, val in kwargs.items():
                setattr(c, attr, val)
        return leaf_cmps

    # Resources
    def get_all_resources_names(self) -> List[str]:
        """Returns a list of all resources names.

        :return: List of all resources names.
        """
        return [r.name for r in self.resources]

    def add_resource(self, res: Resource) -> Resource:
        """Adds resource to model.

        :param res: Resource to add.
        :return: Added Resource.
        """
        res.name = normalize_name(res.name)
        resources_names = self.get_all_resources_names()
        if res.name in resources_names:
            raise BGError(f'Resource "{res.name}" already exists.')
        self.resources.append(res)
        return res

    def get_resource(self, **kwargs) -> Resource:
        """Returns the first resource whose attributes match the kwargs.

        :param kwargs: Desired attributes of a resource.
        :return: Resource.
        """
        return next((res for res in self.resources if matches(res, **kwargs)), None)

    def rename_resource(self, res: Resource, new_name: str) -> Resource:
        """Changes name of a specified resource.

        Raises ResourceStringError when a resource with the new name already exists.

        :param res: Resource
        :param new_name: New name for resource
        :return: Resource with its name changed
        """
        new_name = normalize_name(new_name)
        res_names = self.get_all_resources_names()
        if new_name in res_names and res.name != new_name:  # Allow changing name for the same
            raise BGError(f'Resource with name: "{new_name}" already exists in the taxonomy.')
        res.name = new_name
        return res

    def remove_resource(self, res: Resource) -> Resource:
        """Removes resource from list of resources and all the references to it by its id in Component.produces.

        :param res: Resource to be removed from self.
        :return: Removed Resource.
        """
        for c in self.taxonomy:
            if res.id_ in c.produces:
                del c.produces[res.id_]  # Remove information about production of this resource from components

        self.resources.remove(res)  # Remove component it self
        return res

    def set_resource_production_to_all_components_children(self, cmp: Component, res: Resource, value: int) \
            -> List[Component]:
        """Sets the production of a resource to specific value for all leaf-component children.

        :param self
        :param cmp: Component to set the children production of.
        :param res: Production of this Resource
        :param value: Amount of produced Resource by components
        :return: List of Component's children that are leaves.
        """
        leaf_children = self.get_components_children(cmp, is_leaf=True)
        for c in leaf_children:
            c.produces[res.id_] = value
        return leaf_children

    # Ports
    def add_port(self, prt: Port) -> Port:
        """Adds port to model.

        :param prt: Port to add to the model
        :return: Added port.
        """
        prt.name = normalize_name(prt.name)
        if prt.name in self.get_all_ports_names():
            raise BGError(f'Port "{prt.name}" already exists.')
        self.ports.append(prt)
        return prt

    def rename_port(self, prt: Port, new_name: str) -> Port:
        """Changes port's name.

        :param prt: Port
        :param new_name: New name for port
        :return: Renamed Port.
        """
        new_name = normalize_name(new_name)
        if new_name in self.get_all_ports_names() and prt.name != new_name:     # Allow changing name for the same
            raise BGError(f'Port "{new_name}" already exists.')
        prt.name = new_name
        return prt

    def get_port(self, **kwargs) -> Port:
        """Returns the first port whose attributes match the kwargs.

        :param kwargs: Desired attributes of a port.
        :return: Port.
        """
        return next((prt for prt in self.ports if matches(prt, **kwargs)), None)

    def get_ports_by_ids(self, ids: List[int]) -> List[Port]:
        """Returns a list of ports that have their ids among given ids list.

        :param ids: List of ids of ports to return.
        :return: List of ports.
        """
        return [p for p in self.ports if p.id_ in ids]

    def remove_port(self, prt: Port) -> Port:
        """Removes port from the list of ports and all the references to it by its id in Component.ports.

        :param prt: Port to be removed from self.
        :return: Removed Port.
        """
        for c in self.taxonomy:
            if prt.id_ in c.ports:
                del c.ports[prt.id_]  # Remove information about ports from components

        self.ports.remove(prt)  # Remove port itself
        return prt

    def get_all_ports_names(self) -> List[str]:
        """Returns a list with all ports names."""
        return [p.name for p in self.ports]

    def update_ports_compatibility(self, port, compatible_ports) -> None:
        """Sets the compatibility of a port.

        :param port: The port to set the compatibility of.
        :param compatible_ports: Port is set to be compatible with all ports in "compatible_ports";
            likewise, it sets the ports in "compatible_ports" to be compatible with "port".
        """
        compatible_ports_ids = [p.id_ for p in compatible_ports]
        # If compatibility was removed
        ports_to_remove_ids = [pid for pid in port.compatible_with if pid not in compatible_ports_ids]
        # Remove from the other ports the compatibility with this port
        for pid in ports_to_remove_ids:
            port_ = self.get_port(id_=pid)
            port_.compatible_with.remove(port.id_)
        # Add to other ports compatibility with this port
        for pid in compatible_ports_ids:
            port_ = self.get_port(id_=pid)
            if port.id_ not in port_.compatible_with:
                port_.compatible_with.append(port.id_)
        port.compatible_with = compatible_ports_ids

    def set_ports_amount_to_all_components_children(self, cmp: Component, prt: Port, number: int) \
            -> List[Component]:
        """Sets the number of ports to all leaf children of component.

        :param cmp: Component, whose leaf-children are to be set to have the port.
        :param prt: Port type.
        :param number: Number of ports each of the leaf-children is supposed to have.
        :return: List of children affected.
        """
        leaf_children = self.get_components_children(cmp, is_leaf=True)
        for c in leaf_children:
            c.ports[prt.id_] = number
        return leaf_children

    def get_all_constraints(self) -> List[Any]:
        """Returns a union of sets of simple & complex constraints.

        :param self:
        :return: Set of simple & complex constraints
        """
        return self.simple_constraints + self.complex_constraints

    def get_constraint(self, **kwargs) -> Any:
        """Returns the first constraint whose attributes match the kwargs.
            Note: 'Constraint' might be an instance of either SimpleConstraint or ComplexConstraint

        :param kwargs: Desired attributes of a constraint.
        :return: SimpleConstraint or ComplexConstraint.
        """
        # Look in the simple constraints first
        simple_ctr = next((c for c in self.simple_constraints if matches(c, **kwargs)), None)
        # Then look in the complex ones
        return simple_ctr if simple_ctr is not None \
            else next((c for c in self.complex_constraints if matches(c, **kwargs)), None)

    def get_all_constraints_names(self) -> List[str]:
        """Returns a list with all constraints' names."""
        return [c.name for c in self.get_all_constraints()]

    def add_constraint(self, ctr: Any) -> Tuple[Any, int]:
        """Adds constraint to the self (either to the list of simple constraints or complex).

        :param ctr: Constraint to add to the self
        :return: Added constraint and index of it in the sorted alphabetically union of simple
            and complex constraints (Simple constraints are put first in the union, complex constraints later).
        """
        new_name = normalize_name(ctr.name)
        if ctr.name in self.get_all_constraints_names():
            raise BGError(f'Constraint with the name {ctr.name} already exists.')
        ctr.name = new_name

        if isinstance(ctr, SimpleConstraint):
            if not ctr.components_ids:
                raise BGError('Constraint must contain components.')
            elif ctr.max_ is None and ctr.min_ is None:
                raise BGError('Constraint has to have at least 1 bound.')

            self.simple_constraints.append(ctr)
        elif isinstance(ctr, ComplexConstraint):
            if not ctr.antecedent:
                raise BGError('Constraint must have antecedent.')
            elif not ctr.consequent:
                raise BGError('Constraint must have consequent.')

            self.complex_constraints.append(ctr)
        return ctr, self.get_constraint_index(ctr)

    def edit_constraint(self, edited_ctr: Any) -> Tuple[Any, int]:
        """Updates the constraint data.

        :param edited_ctr: Constraint to edit (SimpleConstraint or ComplexConstraint).
        :return: Edited constraint (SimpleConstraint or ComplexConstraint).
        """
        new_name = normalize_name(edited_ctr.name)
        current_ctr = self.get_constraint(id_=edited_ctr.id_)
        if new_name in self.get_all_constraints_names() and edited_ctr.name != current_ctr.name:
            raise BGError(f'Constraint with the name {edited_ctr.name} already exists.')
        edited_ctr.name = new_name

        if isinstance(edited_ctr, SimpleConstraint):
            if not edited_ctr.components_ids:
                raise BGError('Constraint must contain components.')
            elif edited_ctr.max_ is None and edited_ctr.min_ is None:
                raise BGError('Constraint has to have at least 1 bound.')

            # Replace constraint
            self.simple_constraints.remove(current_ctr)
            self.simple_constraints.append(edited_ctr)
        elif isinstance(edited_ctr, ComplexConstraint):
            if not edited_ctr.antecedent:
                raise BGError('Constraint must have antecedent.')
            elif not edited_ctr.consequent:
                raise BGError('Constraint must have consequent.')

            # Replace constraint
            self.complex_constraints.remove(current_ctr)
            self.complex_constraints.append(edited_ctr)
        return edited_ctr, self.get_constraint_index(edited_ctr)

    def remove_constraint(self, ctr: Any) -> Any:
        """Removes constraint from the self (either from the list of simple constraints or complex).

        :param ctr: Constraint to remove from the self.
        :return: Removed constraint
        """
        if isinstance(ctr, SimpleConstraint):
            self.simple_constraints.remove(ctr)
        else:
            self.complex_constraints.remove(ctr)
        return ctr

    def get_constraint_index(self, ctr: Any) -> int:
        """Returns the index of a constraint in the list created as a union of sorted list of simple constraint
            and sorted list of complex constraints.

        :param ctr: SimpleConstraint or ComplexConstraint
        :return: Index of the constraint.
        """
        sorted_ctrs_names = sorted([p.name for p in self.simple_constraints]) + \
                            sorted([p.name for p in self.complex_constraints])
        return sorted_ctrs_names.index(ctr.name)

    def remove_all_constraints(self) -> None:
        """Removes all constraints from model."""
        self.simple_constraints.clear()
        self.complex_constraints.clear()



