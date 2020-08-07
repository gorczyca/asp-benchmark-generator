from typing import List, Tuple

from model.model import Model
from model.component import Component
from model.port import Port
from model.simple_constraint import SimpleConstraint

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

SYMBOLS = [
    IN_SYMBOL,
    CN_SYMBOL,
    CMP_SYMBOL,
    ROOT_SYMBOL,
    PAN_SYMBOL,
    PPA_SYMBOL,
    PA_SYMBOL,
    PPAT_SYMBOL,
    RES_SYMBOL,
    PRD_SYMBOL,
    PON_SYMBOL,
    PRT_SYMBOL,
    CMB_SYMBOL,
    PO_SYMBOL
]

DOMAIN_STRING = 'Domain'

# TODO: symmetry breaking does not work!!!
# TODO: TRY CHANGING IN INSTEAD OF DOMAIN


def generate_code(model: Model):
    info = __generate_code_info()
    root_code = __generate_root_code(model)
    hierarchy_def = __generate_hierarchy_ontology_definitions()
    hierarchy_code = __generate_hierarchy_code(model)
    associations_def = __generate_associations_ontology_definitions()
    associations_code = __generate_associations_code(model)
    resource_code = __generate_resource_code(model)
    resource_def = __generate_resources_ontology_definitions()
    ports_def = __generate_ports_ontology_definitions()
    ports_code = __generate_ports_code(model)
    simple_constraints_code, complex_constraints_code = __generate_constraints_code(model)
    instances_code = __generate_instances_code(model)
    show_directives = __generate_show_directives()

    return f'{info} \n{root_code}' \
           f'\n%\n% Hierarchy ontology definitions\n%\n{hierarchy_def}\n%\n% Component hierarchy\n%\n{hierarchy_code}' \
           f'\n%\n% Associations ontology definitions\n%\n{associations_def}\n%\n% Associations\n%\n{associations_code}' \
           f'\n%\n% Resources ontology definitions\n%\n{resource_def}\n%\n% Resource\n%\n{resource_code}' \
           f'\n%\n% Ports ontology definitions\n%\n{ports_def}\n%\n% Ports\n%\n{ports_code}' \
           f'\n%\n% Constraints\n%\n%\n% Simple constraints\n%\n{simple_constraints_code}' \
           f'\n%\n% Complex constraints\n%\n{complex_constraints_code}' \
           f'\n%\n% Instances\n%\n{instances_code}' \
           f'\n\n{show_directives}'


def __generate_code_info():
    return f'%\n% THIS CODE IS AUTOMATICALLY GENERATED\n%\n'


def __generate_root_code(model: Model) -> str:
    root_code = ''
    root_code += f'{ROOT_SYMBOL}({CMP_VARIABLE}) :- {model.root_name}({CMP_VARIABLE}).\n'
    root_code += f'{CMP_SYMBOL}({CMP_VARIABLE}) :- {model.root_name}({CMP_VARIABLE}).\n'
    return root_code


def __generate_hierarchy_code(model: Model) -> str:
    hierarchy_code = ''
    for c in model.hierarchy:
        parent_name = CMP_SYMBOL
        if c.parent_id:
            parent: Component = model.get_component_by_id(c.parent_id)
            parent_name = parent.name   # If there is a parent, overwrite :parent_name:

        hierarchy_code += f'{parent_name}({CMP_VARIABLE}) :- {c.name}({CMP_VARIABLE}).\n'
    return hierarchy_code


def __generate_hierarchy_ontology_definitions():
    definitions = ''
    definitions += f'1 {{ {IN_SYMBOL}({CMP_VARIABLE}) : root({CMP_VARIABLE}) }} 1.\n'
    return definitions


def __generate_associations_ontology_definitions():
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
    associations_code = ''
    for c in model.hierarchy:
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
    definitions = ''
    definitions += f':- {RES_SYMBOL}({RES_VARIABLE}), #sum {{ {M_VARIABLE},{CMP_VARIABLE} : ' \
                   f'{PRD_SYMBOL}({CMP_VARIABLE}, {RES_VARIABLE}, {M_VARIABLE}), {IN_SYMBOL}({CMP_VARIABLE}) }} < 0.\n'
    return definitions


def __generate_resource_code(model: Model) -> str:
    res_code = ''
    for r in model.resources:
        res_code += f'{RES_SYMBOL}({RES_VARIABLE}) :- {r.name}({RES_VARIABLE}).\n'
        res_code += f'{r.name}("{r.name}").\n\n'
    for c in model.hierarchy:
        if c.produces:
            for res_id, amount in c.produces.items():
                res = model.get_resource_by_id(res_id)
                res_code += f'{PRD_SYMBOL}({CMP_VARIABLE}, "{res.name}", {amount}) :- ' \
                            f'{c.name}({CMP_VARIABLE}).\n'
    return res_code


def __generate_ports_ontology_definitions() -> str:
    definitions = ''
    definitions += f'0 {{ {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) }} 1 :- {IN_SYMBOL}({PRT_VARIABLE}1), ' \
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
    # TODO: rule added by me. CAUTION
    definitions += f':- {PRT_SYMBOL}({PRT_VARIABLE}), 2 {{ {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}, {N_VARIABLE}) : ' \
                   f'{CMP_SYMBOL}({CMP_VARIABLE}), {PON_SYMBOL}({N_VARIABLE}) }}.\t% TODO: my own rule, check it! \n'
    return definitions


def __get_port_individual_names(cmp: Component, prt: Port) -> List[str]:
    names = []
    for i in range(cmp.ports[prt.id_]):
        names.append(f'{cmp.name}_{prt.name}_{i}')
    return names


def __generate_ports_code(model: Model) -> str:
    prt_code = ''
    for c in model.hierarchy:
        if c.ports:
            for prt_id in c.ports:
                prt = model.get_port_by_id(prt_id)
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
                        prt2 = model.get_port_by_id(compatible_with_id)
                        for c2 in model.hierarchy:
                            if compatible_with_id in c2.ports:
                                prt_individual_names_2 = __get_port_individual_names(c2, prt2)
                                for prt_individual_name_2 in prt_individual_names_2:
                                    prt_code += f'{CMB_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) :- ' \
                                                f'{prt_individual_name}({PRT_VARIABLE}1), {prt_individual_name_2}({PRT_VARIABLE}2). \n'

    return prt_code


def __generate_constraints_ontology_definitions() -> str:
    pass


def __generate_simple_constraint_distinct_partial_code(ctr: SimpleConstraint, model: Model) -> str:
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
    ctr_code = ''
    components = model.get_components_by_ids(ctr.components_ids)
    components_count = len(components)
    for i, cmp in enumerate(components):
        var_no = i + 2
        ctr_code += f'\t{PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}{var_no}, {UNKNOWN_VARIABLE}) : {cmp.name}({CMP_VARIABLE}{var_no})'
        if i == components_count-1:
            ctr_code += '\n'  # Do not put the ';' sign after last part
        else:
            ctr_code += ';\n'
    min_ = '' if not ctr.min_ else ctr.min_
    max_ = '' if not ctr.max_ else ctr.max_
    # C1 is always reserved for the root component
    ctr_code = f'{min_} {{\n{ctr_code}}} {max_}'
    return ctr_code


def __generate_simple_constraints_code(model: Model) -> str:
    ctrs_code = ''
    for ctr in model.simple_constraints:
        partial_ctr_code = __generate_simple_constraint_distinct_partial_code(ctr, model) if ctr.distinct \
            else __generate_simple_constraint_partial_code(ctr, model)
        ctrs_code += f':- {model.root_name}({CMP_VARIABLE}1), {DEFAULT_NEGATION_OPERATOR} {partial_ctr_code}.\n'
    return ctrs_code


def __generate_implication_part(conditions: List[SimpleConstraint], model: Model) -> Tuple[str, List[str]]:
    heads = []
    code = ''
    for condition in conditions:
        condition_code = __generate_simple_constraint_distinct_partial_code(condition, model) \
            if condition.distinct else __generate_simple_constraint_partial_code(condition, model)
        head = condition.name.replace(' ', '_')     # when using names, make sure they don't contain space # TODO: do this to others as well
        code += f'{head} :- {model.root_name}({CMP_VARIABLE}1), {condition_code}.\n'
        heads.append(head)
    return code, heads


def __generate_implication_complete_part(head: str, names: List[str], all_: bool) -> str:
    body = f"{', '.join(names)}" if all_ else f"1 {{ {'; '.join(names)} }}"
    return f'{head} :- {body}.\n'


def __generate_complex_constraints_code(model: Model) -> str:
    ctrs_code = ''
    for ctr in model.complex_constraints:
        antecedents_code, antecedents_heads = __generate_implication_part(ctr.antecedent, model)
        consequents_code, consequents_heads = __generate_implication_part(ctr.consequent, model)
        antecedent_head = f'{ctr.name.replace(" ", "_")}_antecedent'
        antecedent_complete_code = __generate_implication_complete_part(antecedent_head, antecedents_heads, ctr.antecedent_all)
        consequent_head = f'{ctr.name.replace(" ", "_")}_consequent'
        consequent_complete_code = __generate_implication_complete_part(consequent_head, consequents_heads, ctr.consequent_all)
        complete_implication = f':- {antecedent_head}, {DEFAULT_NEGATION_OPERATOR} {consequent_head}.\n'
        ctrs_code += f'{antecedents_code}\n' \
                     f'{consequents_code}\n' \
                     f'{antecedent_complete_code}' \
                     f'\n{consequent_complete_code}' \
                     f'\n{complete_implication}'
    return ctrs_code


def __generate_constraints_code(model: Model) -> Tuple[str, str]:
    simple_constraints_code = __generate_simple_constraints_code(model)
    complex_constraints_code = __generate_complex_constraints_code(model)
    return simple_constraints_code, complex_constraints_code


# TODO: it is not symmetry breaking, it's bounded component's number
def __generate_components_instances_with_symmetry_breaking(name: str, count: int, offset: int) -> str:
    instance_code = f'{name}{DOMAIN_STRING}({offset+1}..{offset+count}).\n'
    instance_code += f'0 {{{name}({CMP_VARIABLE}) : {name}{DOMAIN_STRING}({CMP_VARIABLE})}} {count}.\n'
    instance_code += f'{name}({CMP_VARIABLE}1) :- {name}{DOMAIN_STRING}({CMP_VARIABLE}1), ' \
                     f'{name}{DOMAIN_STRING}({CMP_VARIABLE}2), {name}({CMP_VARIABLE}2), ' \
                     f'{CMP_VARIABLE}1 < {CMP_VARIABLE}2.\n'
    instance_code += f':- {IN_SYMBOL}({CMP_VARIABLE}2), {name}({CMP_VARIABLE}2), {DEFAULT_NEGATION_OPERATOR} ' \
                     f'{IN_SYMBOL}({CMP_VARIABLE}1), {name}({CMP_VARIABLE}1), ' \
                     f'{CMP_VARIABLE}1 < {CMP_VARIABLE}2.\t% TODO own rule for symmetry breaking, check it.\n'
    return instance_code


# TODO: it is not symmetry breaking, it's bounded component's number
def __generate_ports_instances_with_symmetry_breaking(name: str, cmp: Component, prt_number: int, offset: int) -> str:
    instance_code = f'{name}{DOMAIN_STRING}({offset+1}..{offset+cmp.count}).\t% TODO: only for solving\n'
    instance_code += f'{name}({INSTANCE_VARIABLE}+{prt_number * cmp.count}) :- {cmp.name}({INSTANCE_VARIABLE}).\n'
    instance_code += f':- {IN_SYMBOL}({PRT_VARIABLE}2), {name}({PRT_VARIABLE}2), {DEFAULT_NEGATION_OPERATOR} ' \
                     f'{IN_SYMBOL}({PRT_VARIABLE}1), {name}({PRT_VARIABLE}1), ' \
                     f'{PRT_VARIABLE}1 < {PRT_VARIABLE}2.\t% TODO own rule for symmetry breaking, check it.\n'
    return instance_code


def __generate_instances_code(model: Model) -> str:
    inst_code = ''
    inst_code += f'{model.root_name}(0..0).\t% ROOT\n\n'
    offset = 0
    for cmp in model.get_leaf_components():
        if cmp.count:
            # TODO: consider removing condition "if cmp.count > 1"
            if cmp.count > 1 and cmp.symmetry_breaking:     # Symmetry breaking only when there is more than 1 component
                inst_code += __generate_components_instances_with_symmetry_breaking(cmp.name, cmp.count, offset)
            else:
                inst_code += f'{cmp.name}({offset+1}..{offset+cmp.count}).\n'
            offset += cmp.count
            prt_number = 0
            for prt_id, prt_count in cmp.ports.items():
                prt = model.get_port_by_id(prt_id)
                prt_instance_code = ''
                prt_individual_names = __get_port_individual_names(cmp, prt)
                for prt_individual_name in prt_individual_names:
                    prt_number += 1
                    prt_instance_code += \
                        __generate_ports_instances_with_symmetry_breaking(prt_individual_name, cmp, prt_number, offset)\
                        if cmp.symmetry_breaking and cmp.count > 1 \
                        else f'{prt_individual_name}({offset+1}..{offset+cmp.count}).\n'
                            # TODO: 1 consider removing "cmp.count > 1"
                            # TODO: 2 my own rule for symmetry breaking for ports, test it
                    offset += cmp.count
                inst_code += prt_instance_code
        inst_code += '\n'
    return inst_code


def __generate_show_directives() -> str:
    dir_code = ''
    dir_code += f'#show {IN_SYMBOL}/1.\n'
    dir_code += f'#show {CN_SYMBOL}/2.\n'
    return dir_code




















