"""Provides functionality for generation of the ASP code."""

from typing import List, Tuple, Dict

from model import Model, Component, Port, SimpleConstraint
from project_info import PROJECT_WEBSITE, PROJECT_VERSION, AUTHOR_EMAIL

DEFAULT_NEGATION_OPERATOR = 'not'
COUNT_DIRECTIVE = '#count'
SHOW_DIRECTIVE = '#show'
UNKNOWN_VARIABLE = '_'

INSTANCE_VARIABLE = 'X'

CMP_SYMBOL = 'cmp'
ROOT_SYMBOL = 'root'
CMP_VARIABLE = 'C'

IN_SYMBOL = 'in'
N_VARIABLE = 'N'
M_VARIABLE = 'M'

# Associations
PAN_SYMBOL = 'pan'
PPA_SYMBOL = 'ppa'
PA_SYMBOL = 'pa'
PPAT_SYMBOL = 'ppat'
# Resources
RES_SYMBOL = 'res'
RES_VARIABLE = 'R'
PRD_SYMBOL = 'prd'
# Ports
PON_SYMBOL = 'pon'
PRT_SYMBOL = 'prt'
PRT_VARIABLE = 'P'
CMB_SYMBOL = 'cmb'
PO_SYMBOL = 'po'
CN_SYMBOL = 'cn'

# Key in the "shown_predicates_dictionary"
# if value is True then show instances facts
INSTANCES_FACTS = 'Instances facts'

SYMBOLS_WITH_ARITIES = {
    IN_SYMBOL: 1,
    CN_SYMBOL: 2,
    CMP_SYMBOL: 1,
    ROOT_SYMBOL: 1,
    PAN_SYMBOL: 1,
    PPA_SYMBOL: 3,
    PA_SYMBOL: 3,
    PPAT_SYMBOL: 2,
    RES_SYMBOL: 1,
    PRD_SYMBOL: 3,
    PON_SYMBOL: 1,
    PRT_SYMBOL: 1,
    CMB_SYMBOL: 2,
    PO_SYMBOL: 3
}

KEYWORDS = [
    DEFAULT_NEGATION_OPERATOR,
    COUNT_DIRECTIVE,
    SHOW_DIRECTIVE,
    UNKNOWN_VARIABLE,
    INSTANCE_VARIABLE,
    CMP_SYMBOL,
    ROOT_SYMBOL,
    CMP_VARIABLE,
    IN_SYMBOL,
    N_VARIABLE,
    M_VARIABLE,
    PAN_SYMBOL,
    PPA_SYMBOL,
    PA_SYMBOL,
    PPAT_SYMBOL,
    RES_SYMBOL,
    RES_VARIABLE,
    PRD_SYMBOL,
    PON_SYMBOL,
    PRT_SYMBOL,
    PRT_VARIABLE,
    CMB_SYMBOL,
    PO_SYMBOL,
    CN_SYMBOL,
]

SYMBOLS = list(SYMBOLS_WITH_ARITIES.keys())

DOMAIN_STRING = 'Domain'


def generate_code(model: Model, show_all_predicates: bool, shown_predicates_dict: Dict[str, bool]) -> str:
    """Generates ASP encoding of the model.

    :param model: Model to generate the encoding of.
    :param show_all_predicates: Whether to show all predicates or the selected ones.
    :param shown_predicates_dict:   Dictionary of type predicate_symbol: show?
    :return: Model's ASP encoding.
    """
    info = __generate_code_info()
    root_code = __generate_root_code(model)
    taxonomy_def = __generate_taxonomy_ontology_definitions()
    taxonomy_code = __generate_taxonomy_code(model)
    associations_def = __generate_associations_ontology_definitions()
    associations_code = __generate_associations_code(model)
    resource_code = __generate_resources_code(model)
    resource_def = __generate_resources_ontology_definitions()
    ports_def = __generate_ports_ontology_definitions()
    ports_code = __generate_ports_code(model)
    simple_constraints_code, complex_constraints_code = __generate_constraints_code(model)
    instances_code, instances_predicates = __generate_instances_code(model)
    show_directives = __generate_show_directives(show_all_predicates, shown_predicates_dict, instances_predicates)

    return f'{info} \n{root_code}' \
           f'\n%\n% Taxonomy ontology definitions\n%\n{taxonomy_def}\n%\n% Component taxonomy\n%\n{taxonomy_code}' \
           f'\n%\n% Associations ontology definitions\n%\n{associations_def}\n%\n% Associations\n%\n{associations_code}' \
           f'\n%\n% Resources ontology definitions\n%\n{resource_def}\n%\n% Resource\n%\n{resource_code}' \
           f'\n%\n% Ports ontology definitions\n%\n{ports_def}\n%\n% Ports\n%\n{ports_code}' \
           f'\n%\n% Constraints\n%\n%\n% Simple constraints\n%\n{simple_constraints_code}' \
           f'\n%\n% Complex constraints\n%\n{complex_constraints_code}' \
           f'\n%\n% Instances\n%\n{instances_code}' \
           f'\n\n{show_directives}'


def __generate_code_info() -> str:
    """Creates header comment for the generated file.

    :return: Header comment.
    """
    info = ''
    info += f'%=====================================================================================\n'
    info += f'%\n'
    info += f'% The following ASP code has been generated by the "Benchmark Generator" version {PROJECT_VERSION}.\n'
    info += f'% In case of problems please refer to:\n'
    info += f'% \t{PROJECT_WEBSITE}\n'
    info += f'% or write an email to:\n'
    info += f'% \t{AUTHOR_EMAIL}\n'
    info += f'%\n'
    info += f'%=====================================================================================\n'
    return info


def __generate_root_code(model: Model) -> str:
    """Generates root component's code.

    :param model: Model.
    :return: Root component's code.
    """
    root_code = f'{ROOT_SYMBOL}({CMP_VARIABLE}) :- {model.root_name}({CMP_VARIABLE}).\n'
    root_code += f'{CMP_SYMBOL}({CMP_VARIABLE}) :- {model.root_name}({CMP_VARIABLE}).\n'
    return root_code


def __generate_taxonomy_code(model: Model) -> str:
    """Generates taxonomy of components' code.

    :param model: Model
    :return: Taxonomy of components' code.
    """
    taxonomy_code = ''
    for c in model.taxonomy:
        parent_name = CMP_SYMBOL
        if c.parent_id:
            parent: Component = model.get_component(id_=c.parent_id)
            parent_name = parent.name   # If there is a parent, overwrite :parent_name:

        taxonomy_code += f'{parent_name}({CMP_VARIABLE}) :- {c.name}({CMP_VARIABLE}).\n'
    return taxonomy_code


def __generate_taxonomy_ontology_definitions():
    """Generates ontology definitions regarding taxonomy of components.
    (Ontology definitions are the same for every instance of configuration problem.)

    :return: Ontology definitions of taxonomy.
    """
    definitions = f'1 {{ {IN_SYMBOL}({CMP_VARIABLE}) : root({CMP_VARIABLE}) }} 1.\n'
    return definitions


def __generate_associations_ontology_definitions():
    """Generates ontology definitions regarding associations.
    (Ontology definitions are the same for every instance of configuration problem.)

    :return: Ontology definitions of associations.
    """
    definitions = ''
    definitions += f'{IN_SYMBOL}({CMP_VARIABLE}2) :- {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, {N_VARIABLE}), ' \
                   f'{CMP_SYMBOL}({CMP_VARIABLE}1), {CMP_SYMBOL}({CMP_VARIABLE}2), {PAN_SYMBOL}({N_VARIABLE}).\n'
    definitions += f':- {CMP_SYMBOL}({CMP_VARIABLE}2), 2 {{ {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, ' \
                   f'{N_VARIABLE}) : {CMP_SYMBOL}({CMP_VARIABLE}1), {PAN_SYMBOL}({N_VARIABLE}) }}.\n'
    definitions += f'{PPAT_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2) :- ' \
                   f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, {N_VARIABLE}), {PAN_SYMBOL}({N_VARIABLE}).\n'
    definitions += f'{PPAT_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}3) :- {PPA_SYMBOL}({CMP_VARIABLE}1, ' \
                   f'{CMP_VARIABLE}2, {N_VARIABLE}), {CMP_SYMBOL}({CMP_VARIABLE}3), {PPAT_SYMBOL}({CMP_VARIABLE}2, ' \
                   f'{CMP_VARIABLE}3), {PAN_SYMBOL}({N_VARIABLE}).\n'
    definitions += f':- {PPAT_SYMBOL}({CMP_VARIABLE}, {CMP_VARIABLE}), {CMP_SYMBOL}({CMP_VARIABLE}).\n'
    return definitions


def __generate_associations_code(model: Model) -> str:
    """Generates associations' code.

    :param model: Model.
    :return: Associations' code.
    """
    associations_code = ''
    for c in model.taxonomy:
        if c.association:
            associations_code += f'{PAN_SYMBOL}("{c.name}").\n'
            associations_code += f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") :- ' \
                                 f'{model.root_name}({CMP_VARIABLE}1), {c.name}({CMP_VARIABLE}2).\n'
            min_ = '' if not c.association.min_ else c.association.min_
            max_ = '' if not c.association.max_ else c.association.max_
            associations_code += f'{min_} {{ {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") : ' \
                                 f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") }} {max_} :- ' \
                                 f'{IN_SYMBOL}({CMP_VARIABLE}1), {model.root_name}({CMP_VARIABLE}1).\n'
    return associations_code


def __generate_resources_ontology_definitions() -> str:
    """Generates ontology definitions regarding taxonomy of components.
    (Ontology definitions are the same for every instance of configuration problem.)

    :return: Ontology definitions of taxonomy.
    """
    definitions = ''
    definitions += f':- {RES_SYMBOL}({RES_VARIABLE}), #sum {{ {M_VARIABLE},{CMP_VARIABLE} : ' \
                   f'{PRD_SYMBOL}({CMP_VARIABLE}, {RES_VARIABLE}, {M_VARIABLE}), {IN_SYMBOL}({CMP_VARIABLE}) }} < 0.\n'
    return definitions


def __generate_resources_code(model: Model) -> str:
    """Generates resources' code.

    :param model: Model
    :return: Resources' code.
    """
    res_code = ''
    for r in model.resources:
        res_code += f'{RES_SYMBOL}({RES_VARIABLE}) :- {r.name}({RES_VARIABLE}).\n'
        res_code += f'{r.name}("{r.name}").\n\n'
    for c in model.taxonomy:
        if c.produces:
            for res_id, amount in c.produces.items():
                res = model.get_resource(id_=res_id)
                res_code += f'{PRD_SYMBOL}({CMP_VARIABLE}, "{res.name}", {amount}) :- ' \
                            f'{c.name}({CMP_VARIABLE}).\n'
    return res_code


def __generate_ports_ontology_definitions() -> str:
    """Generates ontology definitions regarding taxonomy of components.
    (Ontology definitions are the same for every instance of configuration problem.)

    :return: Ontology definitions of taxonomy.
    """
    definitions = f'0 {{ {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) }} 1 :- {IN_SYMBOL}({PRT_VARIABLE}1), ' \
                   f'{IN_SYMBOL}({PRT_VARIABLE}2), {CMB_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2).\n'
    definitions += f'{CN_SYMBOL}({PRT_VARIABLE}2, {PRT_VARIABLE}1) :- {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2), ' \
                   f'{PRT_SYMBOL}({PRT_VARIABLE}1), {PRT_SYMBOL}({PRT_VARIABLE}2).\n'
    definitions += f':- {PRT_SYMBOL}({PRT_VARIABLE}1), ' \
                   f'2 {{ {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) : {PRT_SYMBOL}({PRT_VARIABLE}2) }}.\n'
    definitions += f':- {PRT_SYMBOL}({PRT_VARIABLE}), {CN_SYMBOL}({PRT_VARIABLE}, {PRT_VARIABLE}).\n'
    definitions += f'{IN_SYMBOL}({PRT_VARIABLE}) :- {CMP_SYMBOL}({CMP_VARIABLE}), {PON_SYMBOL}({N_VARIABLE}), ' \
                   f'{PRT_SYMBOL}({PRT_VARIABLE}), {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}, {N_VARIABLE}).\n'
    definitions += f':- {CMP_SYMBOL}({CMP_VARIABLE}), {PRT_SYMBOL}({PRT_VARIABLE}1), {PON_SYMBOL}({N_VARIABLE}1), ' \
                   f'{PRT_SYMBOL}({PRT_VARIABLE}2), {PON_SYMBOL}({N_VARIABLE}2), {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}1, {N_VARIABLE}1), ' \
                   f'{PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}2, {N_VARIABLE}2), {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2).\n'
    # TODO: rule added by me. Requires testing.
    definitions += f':- {PRT_SYMBOL}({PRT_VARIABLE}), 2 {{ {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}, {N_VARIABLE}) : ' \
                   f'{CMP_SYMBOL}({CMP_VARIABLE}), {PON_SYMBOL}({N_VARIABLE}) }}.\n'
    return definitions


def __get_port_individual_names(cmp: Component, prt: Port) -> List[str]:
    """Generates the list of individual names of port's instances
    (useful whenever a component has more than 1 instance of port)

    :param cmp: Component that has the port.
    :param prt: Port
    :return: List of individual names of port's instances.
    """
    names = []
    for i in range(cmp.ports[prt.id_]):
        names.append(f'{cmp.name}_{prt.name}_{i}')
    return names


def __generate_ports_code(model: Model) -> str:
    """Generates ports' code.

    :param model: Model
    :return: Ports' code.
    """
    prt_code = ''
    for c in model.taxonomy:
        if c.ports:
            for prt_id in c.ports:
                prt = model.get_port(id_=prt_id)
                prt_individual_names = __get_port_individual_names(c, prt)
                for prt_individual_name in prt_individual_names:
                    prt_code += f'{PRT_SYMBOL}({PRT_VARIABLE}) :- {prt_individual_name}({PRT_VARIABLE}).\n'
                    prt_code += f'{PON_SYMBOL}("{prt_individual_name}").\n'
                    # Port on a device
                    prt_code += f'1 {{ {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}, "{prt_individual_name}") : ' \
                                f'{prt_individual_name}({PRT_VARIABLE}) }} 1 :- ' \
                                f'{IN_SYMBOL}({CMP_VARIABLE}), {c.name}({CMP_VARIABLE}).\n'
                    # Force connection
                    if prt.force_connection:
                        prt_code += f':- {c.name}({CMP_VARIABLE}), {prt_individual_name}({PRT_VARIABLE}1), ' \
                                    f'{PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}1, "{prt_individual_name}"), ' \
                                    f'{{ {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) : {PRT_SYMBOL}({PRT_VARIABLE}2) }} 0.\n'
                    # Compatibility
                    for compatible_with_id in prt.compatible_with:
                        prt2 = model.get_port(id_=compatible_with_id)
                        for c2 in model.taxonomy:
                            if compatible_with_id in c2.ports:
                                prt_individual_names_2 = __get_port_individual_names(c2, prt2)
                                for prt_individual_name_2 in prt_individual_names_2:
                                    prt_code += f'{CMB_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) :- ' \
                                                f'{prt_individual_name}({PRT_VARIABLE}1), {prt_individual_name_2}({PRT_VARIABLE}2). \n'

    return prt_code


def __generate_simple_constraint_distinct_partial_code(ctr: SimpleConstraint, model: Model) -> str:
    """Generates a part (condition / body of a rule) of simple constraint's code. Used when distinct property
    of the constraint is set to True.

    :param ctr: Constraint.
    :param model: Model.
    :return: Part of simple constraint's code.
    """
    ctr_code = ''
    components = model.get_components_by_ids(ctr.components_ids)
    components_count = len(components)
    for i, cmp in enumerate(components):
        var_no = i + 2
        ctr_code += f'\t{cmp.name} : {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}{var_no}, {UNKNOWN_VARIABLE}), {cmp.name}({var_no})'
        if i == components_count-1:
            ctr_code += '\n'    # Do not put the ';' sign after last part
        else:
            ctr_code += ';\n'
    min_ = '' if not ctr.min_ else ctr.min_
    max_ = '' if not ctr.max_ else ctr.max_
    # C1 is always reserved for the root component
    ctr_code = f'{min_} {COUNT_DIRECTIVE} {{\n{ctr_code}}} {max_}'
    return ctr_code


def __generate_simple_constraint_partial_code(ctr: SimpleConstraint, model: Model) -> str:
    """Generates a part (condition / body of a rule) of simple constraint's code. Used when distinct property
    of the constraint is set to False.

    :param ctr: Constraint.
    :param model: Model.
    :return: Part of simple constraint's code.
    """
    ctr_code = ''
    components = model.get_components_by_ids(ctr.components_ids)
    components_count = len(components)
    for i, cmp in enumerate(components):
        var_no = i + 2
        ctr_code += f'\t{PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}{var_no}, {UNKNOWN_VARIABLE}) : {cmp.name}({CMP_VARIABLE}{var_no})'
        if i == components_count - 1:
            ctr_code += '\n'  # Do not put the ';' sign after last part
        else:
            ctr_code += ';\n'
    min_ = '' if not ctr.min_ else ctr.min_
    max_ = '' if not ctr.max_ else ctr.max_
    # C1 is always reserved for the root component
    ctr_code = f'{min_} {{\n{ctr_code}}} {max_}'
    return ctr_code


def __generate_simple_constraints_code(model: Model) -> str:
    """Generates simple constraints' code.

    :param model: Model
    :return: Simple constraints' code.
    """
    ctrs_code = ''
    for ctr in model.simple_constraints:
        partial_ctr_code = __generate_simple_constraint_distinct_partial_code(ctr, model) if ctr.distinct \
            else __generate_simple_constraint_partial_code(ctr, model)
        ctrs_code += f':- {model.root_name}({CMP_VARIABLE}1), {DEFAULT_NEGATION_OPERATOR} {partial_ctr_code}.\n'
    return ctrs_code


def __generate_implication_part(conditions: List[SimpleConstraint], model: Model) -> Tuple[str, List[str]]:
    """Generates a part of the implication. For each SimpleConstraint it creates a rule stating that a new fact
    is satisfied if so is its condition. These new facts are later used to create the complex constraints.

    :param conditions: List of conditions represented as SimpleConstraints
    :param model: Model
    :return: Tuple of the form (code generated with new rules, list of new facts [heads of the new rules])
    """
    heads = []
    code = ''
    for condition in conditions:
        condition_code = __generate_simple_constraint_distinct_partial_code(condition, model) \
            if condition.distinct else __generate_simple_constraint_partial_code(condition, model)
        head = condition.name
        code += f'{head} :- {model.root_name}({CMP_VARIABLE}1), {condition_code}.\n'
        heads.append(head)
    return code, heads


def __generate_implication_complete_part(head: str, names: List[str], all_: bool) -> str:
    """Generates a complete part of the Complex Constraint's rule (either its antecedent or consequent)

    :param head: Head of the generated rule.
    :param names: List of conditions.
    :param all_: Whether all or only one of the facts in 'names' have to be satisfied so that head is derived.
    :return:
    """
    body = f"{', '.join(names)}" if all_ else f"1 {{ {'; '.join(names)} }}"
    return f'{head} :- {body}.\n'


def __generate_complex_constraints_code(model: Model) -> str:
    """Generates complex constraints' code.

    :param model: Model
    :return: Complex constraints' code.
    """
    ctrs_code = ''
    for ctr in model.complex_constraints:
        antecedents_code, antecedents_heads = __generate_implication_part(ctr.antecedent, model)
        consequents_code, consequents_heads = __generate_implication_part(ctr.consequent, model)
        antecedent_head = f'{ctr.name.replace(" ", "_")}_antecedent'
        antecedent_complete_code = __generate_implication_complete_part(antecedent_head, antecedents_heads,
                                                                        ctr.antecedent_all)
        consequent_head = f'{ctr.name.replace(" ", "_")}_consequent'
        consequent_complete_code = __generate_implication_complete_part(consequent_head, consequents_heads,
                                                                        ctr.consequent_all)
        complete_implication = f':- {antecedent_head}, {DEFAULT_NEGATION_OPERATOR} {consequent_head}.\n'
        ctrs_code += f'{antecedents_code}\n' \
                     f'{consequents_code}\n' \
                     f'{antecedent_complete_code}' \
                     f'\n{consequent_complete_code}' \
                     f'\n{complete_implication}'
    return ctrs_code


def __generate_constraints_code(model: Model) -> Tuple[str, str]:
    """Generates constraints (both simple & complex).

    :param model: Model
    :return: Simple constraints' code; Complex constraints' code
    """
    simple_constraints_code = __generate_simple_constraints_code(model)
    complex_constraints_code = __generate_complex_constraints_code(model)
    return simple_constraints_code, complex_constraints_code


def __generate_variable_number_of_components_instances(cmp: Component, count: int, offset: int) -> str:
    """Generates a rule expressing the variable (bounded) number of component's instances.

    :param cmp: Component
    :param count: Maximal number of component's instances (max - min).
    :param offset: Instances id offset.
    :return: Rule expressing variable number of component's instances.
    """
    instance_code = f'{cmp.name}{DOMAIN_STRING}({offset+1}..{offset+count}).\n'
    instance_code += f'{cmp.min_count} {{{cmp.name}({CMP_VARIABLE}) : {cmp.name}{DOMAIN_STRING}({CMP_VARIABLE})}} {cmp.max_count}.\n'
    instance_code += f'{cmp.name}({CMP_VARIABLE}1) :- {cmp.name}{DOMAIN_STRING}({CMP_VARIABLE}1), ' \
                     f'{cmp.name}{DOMAIN_STRING}({CMP_VARIABLE}2), {cmp.name}({CMP_VARIABLE}2), ' \
                     f'{CMP_VARIABLE}1 < {CMP_VARIABLE}2.\n'
    return instance_code


def __generate_variable_number_of_port_instances(name: str, cmp: Component, count: int, prt_number: int, offset: int) \
        -> str:
    """Generates a rule expressing the variable (bounded) number of port instances.

    :param name: Name of the port's individual.
    :param cmp: Component the port belongs to.
    :param count: Maximal number of component's instances (max - min).
    :param prt_number: Index of the port.
    :param offset:  Instances id offset.
    :return: Rule expressing variable number of port instances.
    """
    instance_code = f'{name}{DOMAIN_STRING}({offset+1}..{offset+count}).\n'     # Rule is added for solving purposes
    instance_code += f'{name}({INSTANCE_VARIABLE}+{prt_number * count}) :- {cmp.name}({INSTANCE_VARIABLE}), ' \
                     f'{name}{DOMAIN_STRING}({INSTANCE_VARIABLE}+{prt_number * count}).\n'  # TODO: rule added by me. Requires testing.
    return instance_code


def __generate_symmetry_breaking_rule(name: str, variable: str = CMP_VARIABLE) -> str:
    """Generates symmetry breaking rule.

    :param name: Component's name to generate the symmetry breaking rule of.
    :param variable: Variable to use.
    :return: Symmetry breaking rule for the given component's name.
    """
    symm_breaking_rule = f':- {IN_SYMBOL}({variable}2), {name}({variable}2), {DEFAULT_NEGATION_OPERATOR} ' \
                         f'{IN_SYMBOL}({variable}1), {name}({variable}1), ' \
                         f'{variable}1 < {variable}2.\n'        # TODO: rule added by me. Requires testing.
    return symm_breaking_rule


def __generate_instances_code(model: Model) -> Tuple[str, List[str]]:
    """Generates instances code.

    :param model: Model.
    :return: Instances code; List of instances predicate symbols.
    """
    inst_predicates = []
    inst_code = ''
    inst_code += f'{model.root_name}(0..0).\t% ROOT\n\n'
    offset = 0
    for cmp in model.get_components():
        count = 0
        if cmp.count:
            count = cmp.count
            inst_code += f'{cmp.name}({offset + 1}..{offset + count}).\n'
            inst_predicates.append(cmp.name)
        elif cmp.min_count is not None and cmp.max_count is not None:
            count = cmp.max_count - cmp.min_count
            inst_code += __generate_variable_number_of_components_instances(cmp, count, offset)
            inst_predicates.append(f'{cmp.name}{DOMAIN_STRING}')
            inst_predicates.append(cmp.name)

        if cmp.symmetry_breaking:
            inst_code += __generate_symmetry_breaking_rule(cmp.name)

        if count:   # If component appears in configuration
            inst_predicates.append(cmp.name)
            offset += count
            prt_number = 0
            for prt_id, prt_count in cmp.ports.items():
                prt = model.get_port(id_=prt_id)
                prt_instance_code = ''
                prt_individual_names = __get_port_individual_names(cmp, prt)
                for prt_individual_name in prt_individual_names:
                    prt_number += 1
                    if cmp.count:
                        prt_instance_code += f'{prt_individual_name}({offset+1}..{offset+cmp.count}).\n'
                    else:
                        prt_instance_code += __generate_variable_number_of_port_instances(prt_individual_name, cmp,
                                                                                          count, prt_number, offset)
                        inst_predicates.append(f'{prt_individual_name}{DOMAIN_STRING}')

                    inst_predicates.append(prt_individual_name)
                    offset += count
                    if cmp.symmetry_breaking:
                        prt_instance_code += __generate_symmetry_breaking_rule(prt_individual_name,
                                                                               variable=PRT_VARIABLE)
                inst_code += prt_instance_code
        inst_code += '\n'
    return inst_code, inst_predicates


def __generate_show_directives(show_all_predicates: bool, shown_predicates_dict: Dict[str, bool],
                               instances_predicates: List[str]) \
        -> str:
    """Generates the '#show' directives, according to user's selection of predicates.

    :param show_all_predicates: If this is set to true then no directives are generated,
        resulting in showing all possible predicates.
    :param shown_predicates_dict: A dictionary of type predicate_symbol: show?
    :param instances_predicates: Predicates symbols representing instances.
    :return: '#show' directives code.
    """
    if show_all_predicates:
        return ''

    dir_code = ''
    if shown_predicates_dict[INSTANCES_FACTS]:
        dir_code += '% Instances facts:\n'
        for pred in instances_predicates:
            dir_code += f'{SHOW_DIRECTIVE} {pred}/1.\n'
    for symbol in SYMBOLS:
        if shown_predicates_dict[symbol]:
            dir_code += f'#show {symbol}/{SYMBOLS_WITH_ARITIES[symbol]}.\n'
    return dir_code
