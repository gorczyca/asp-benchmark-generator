from typing import List, Tuple

from model.complex_constraint import ComplexConstraint
from model.model import Model
from model.component import Component
from model.port import Port
from model.simple_constraint import SimpleConstraint

NEWLINE_SYMBOL = '\n'
DEFAULT_NEGATION_SYMBOL = 'not'
COUNT_DIRECTIVE = '#count'
UNKNOWN_VARIABLE = '_'

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

# TODO: remove this newline symbol


def generate_code(model: Model, root_name: str):
    info = __generate_code_info()
    root_code = __generate_root_code(root_name)
    hierarchy_def = __generate_hierarchy_ontology_definitions()
    hierarchy_code = __generate_hierarchy_code(model)
    associations_def = __generate_associations_ontology_definitions()
    associations_code = __generate_associations_code(model, root_name)
    resource_code = __generate_resource_code(model)
    resource_def = __generate_resources_ontology_definitions()
    ports_def = __generate_ports_ontology_definitions()
    ports_code = __generate_ports_code(model)

    return f'{info} \n{root_code}' \
           f'\n%\n% Hierarchy ontology definitions\n%\n{hierarchy_def}\n%\n% Component hierarchy\n%\n{hierarchy_code}' \
           f'\n%\n% Associations ontology definitions\n%\n{associations_def}\n%\n% Associations\n%\n{associations_code}' \
           f'\n%\n% Resources ontology definitions\n%\n{resource_def}\n%\n% Resource\n%\n{resource_code}' \
           f'\n%\n% Ports ontology definitions\n%\n{ports_def}\n%\n% Ports\n%\n{ports_code}'


def __generate_code_info():
    return f'%{NEWLINE_SYMBOL}% THIS CODE IS AUTOMATICALLY GENERATED{NEWLINE_SYMBOL}%{NEWLINE_SYMBOL}'


def __generate_root_code(root_name: str) -> str:
    root_code = ''
    root_code += f'{ROOT_SYMBOL}({CMP_VARIABLE}) :- {root_name}({CMP_VARIABLE}).{NEWLINE_SYMBOL}'
    root_code += f'{CMP_SYMBOL}({CMP_VARIABLE}) :- {root_name}({CMP_VARIABLE}).{NEWLINE_SYMBOL}'
    return root_code


def __generate_hierarchy_code(model: Model) -> str:
    hierarchy_code = ''
    for c in model.hierarchy:
        parent_name = CMP_SYMBOL
        if c.parent_id:
            parent: Component = model.get_component_by_id(c.parent_id)
            parent_name = parent.name   # If there is a parent, overwrite :parent_name:

        hierarchy_code += f'{parent_name}({CMP_VARIABLE}) :- {c.name}({CMP_VARIABLE}).{NEWLINE_SYMBOL}'
    return hierarchy_code


def __generate_hierarchy_ontology_definitions():
    definitions = ''
    definitions += f'1 {{{IN_SYMBOL}({CMP_VARIABLE}) : root({CMP_VARIABLE}) }} 1.\n'
    return definitions


def __generate_associations_ontology_definitions():
    definitions = ''
    definitions += f'{IN_SYMBOL}({CMP_VARIABLE}2) :- {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, {N_VARIABLE}), ' \
                   f'{CMP_SYMBOL}({CMP_VARIABLE}1), {CMP_SYMBOL}({CMP_VARIABLE}2), {PAN_SYMBOL}({N_VARIABLE}).\n'
    definitions += f':- {CMP_SYMBOL}({CMP_VARIABLE}2), 2 {{{PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, {N_VARIABLE}) }}.\n'
    definitions += f'{PPAT_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2) :- {PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, _).\n'
    definitions += f'{PPAT_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}3) :- {PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, _), {CMP_SYMBOL}({CMP_VARIABLE}3), {PPAT_SYMBOL}({CMP_VARIABLE}2, {CMP_VARIABLE}3).\n'
    definitions += f':- {PPAT_SYMBOL}({CMP_VARIABLE}, {CMP_VARIABLE}), {CMP_SYMBOL}({CMP_VARIABLE}).\n'
    return definitions


def __generate_associations_code(model: Model, root_name: str) -> str:
    associations_code = ''
    for c in model.hierarchy:
        if c.association:
            associations_code += f'{PAN_SYMBOL}("{c.name}").{NEWLINE_SYMBOL}'
            associations_code += f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") :- ' \
                                 f'{root_name}({CMP_VARIABLE}1), {c.name}({CMP_VARIABLE}2).{NEWLINE_SYMBOL}'
            min_ = '' if not c.association.min_ else c.association.min_
            max_ = '' if not c.association.max_ else c.association.max_
            associations_code += f'{min_} {{{PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") : ' \
                                 f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}")}} {max_} :- ' \
                                 f'{IN_SYMBOL}({CMP_VARIABLE}1), {root_name}({CMP_VARIABLE}2).{NEWLINE_SYMBOL}'
    return associations_code


def __generate_resources_ontology_definitions() -> str:
    definitions = ''
    definitions += f'{RES_SYMBOL}({RES_VARIABLE}), #sum {{{M_VARIABLE}, {CMP_VARIABLE} : ' \
                   f'{PRD_SYMBOL}({CMP_VARIABLE}, {RES_VARIABLE}, {M_VARIABLE}), {IN_SYMBOL}({CMP_VARIABLE}) }} < 0.\n'
    return definitions


def __generate_resource_code(model: Model) -> str:
    res_code = ''
    for r in model.resources:
        res_code += f'{RES_SYMBOL}({RES_VARIABLE}) :- {r.name}({RES_VARIABLE}).{NEWLINE_SYMBOL}'
    for c in model.hierarchy:
        if c.produces:
            for res_id, amount in c.produces.items():
                res = model.get_resource_by_id(res_id)
                res_code += f'{PRD_SYMBOL}({CMP_VARIABLE}, "{res.name}", {amount}) :- ' \
                            f'{c.name}({CMP_VARIABLE}).{NEWLINE_SYMBOL}'
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
                   f'{PRT_SYMBOL}({PRT_VARIABLE}2), {PON_SYMBOL}({N_VARIABLE}2), {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}1, {N_VARIABLE}1)' \
                   f'{PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}2, {N_VARIABLE}2), {CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2).\n'
    return definitions


def __generate_ports_code(model: Model) -> str:
    def __get_port_individual_names(cmp_: Component, prt_: Port) -> List[str]:
        names_ = []
        for i_ in range(cmp_.ports[prt_.id_]):
            names_.append(f'{cmp_.name}_{prt_.name}_{i_}')
        return names_

    prt_code = ''
    for c in model.hierarchy:
        if c.ports:
            for prt_id in c.ports:
                prt = model.get_port_by_id(prt_id)
                prt_individual_names = __get_port_individual_names(c, prt)
                for prt_individual_name in prt_individual_names:
                    prt_code += f'{PON_SYMBOL}("{prt_individual_name}").{NEWLINE_SYMBOL}'
                    prt_code += f'{PRT_SYMBOL}({PRT_VARIABLE}) :- {prt_individual_name}({PRT_VARIABLE}).{NEWLINE_SYMBOL}'
                    # Compatibility
                    for compatible_with_id in prt.compatible_with:
                        prt2 = model.get_port_by_id(compatible_with_id)
                        for c2 in model.hierarchy:
                            if compatible_with_id in c2.ports:
                                prt_individual_names_2 = __get_port_individual_names(c2, prt2)
                                for prt_individual_name_2 in prt_individual_names_2:
                                    prt_code += f'{CMB_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) :- ' \
                                                f'{prt_individual_name}({PRT_VARIABLE}1), {prt_individual_name_2}({PRT_VARIABLE}2). {NEWLINE_SYMBOL}'
                    # Port on device
                    prt_code += f'1 {{ {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}, "{prt_individual_name}") : ' \
                                f'{prt_individual_name}({PRT_VARIABLE}) }} 1 :- ' \
                                f'{IN_SYMBOL}({CMP_VARIABLE}), {c.name}({CMP_VARIABLE}).{NEWLINE_SYMBOL}'
                    # Force connection
                    if prt.force_connection:
                        prt_code += f':- {c.name}({CMP_VARIABLE}), {prt_individual_name}({PRT_VARIABLE}1), ' \
                                    f'{PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}1, "{prt_individual_name}"), ' \
                                    f'{{{CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) : {PRT_SYMBOL}({PRT_VARIABLE}2)}} 0. {NEWLINE_SYMBOL}'
    return prt_code


def __generate_constraints_ontology_definitions() -> str:
    pass


def __generate_simple_constraint_distinct_partial_code(ctr: SimpleConstraint, model: Model) -> str:
    ctr_code = ''
    components = model.get_components_by_ids(ctr.components_ids)
    for i, cmp in enumerate(components):
        var_no = i + 2
        ctr_code += f'{cmp.name} : {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}{var_no}, {UNKNOWN_VARIABLE}), {cmp.name}({var_no});\n'
    min_ = '' if not ctr.min_ else ctr.min_
    max_ = '' if not ctr.max_ else ctr.max_
    # C1 is always reserved for the root component
    ctr_code = f'{min_} {COUNT_DIRECTIVE} {{ \n{ctr_code} }} {max_}'
    return ctr_code


def __generate_simple_constraint_partial_code(ctr: SimpleConstraint, model: Model) -> str:
    ctr_code = ''
    components = model.get_components_by_ids(ctr.components_ids)
    for i, cmp in enumerate(components):
        var_no = i + 2
        ctr_code += f'{PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}{var_no}, {UNKNOWN_VARIABLE}) : {cmp.name}({var_no});\n'
    min_ = '' if not ctr.min_ else ctr.min_
    max_ = '' if not ctr.max_ else ctr.max_
    # C1 is always reserved for the root component
    ctr_code = f'{min_} {{ \n{ctr_code} }} {max_}'
    return ctr_code


def __generate_simple_constraints_code(model: Model, root_name: str) -> str:
    ctrs_code = ''
    for ctr in model.simple_constraints:
        partial_ctr_code = __generate_simple_constraint_distinct_partial_code(ctr, model) if ctr.distinct \
            else __generate_simple_constraint_partial_code(ctr, model)
        ctrs_code += f'{DEFAULT_NEGATION_SYMBOL} {partial_ctr_code}.\n'
    return ctrs_code


def __generate_implication_part(conditions: List[SimpleConstraint], model: Model) -> Tuple[str, List[str]]:
    heads = []
    code = ''
    for condition in conditions:
        condition_code = __generate_simple_constraint_distinct_partial_code(condition, model) \
            if condition.distinct else __generate_simple_constraint_partial_code(condition, model)
        head = condition.name.replace(' ', '_')  # when using names, make sure they don't contain space # TODO: do this to others as well
        code += f'{head} :- {condition_code}.\n'
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
        complete_implication = f'{antecedent_head}, {DEFAULT_NEGATION_SYMBOL} {consequent_head}.'
        # TODO: add comments to generated code
        ctrs_code += f'{antecedents_code}\n{consequents_code}\n{antecedent_complete_code}\n{consequent_complete_code}'



def __generate_constraints_code(model: Model) -> str:
    # Simple constraints
    pass

def __generate_instances_code(model: Model) -> str:
    pass


















