from typing import List, Tuple

from model.model import Model
from model.component import Component
from model.port import Port
from model.simple_constraint import SimpleConstraint

DEFAULT_NEGATION_SYMBOL = 'not'
COUNT_DIRECTIVE = '#count'
UNKNOWN_VARIABLE = '_'

INSTANCE_VARIABLE = 'X'

CMP_SYMBOL = 'cmp'
ROOT_SYMBOL = 'root'
CMP_VARIABLE = 'C'

IN_SYMBOL = 'in'
N_VARIABLE = 'N'
M_VARIABLE = 'M'
SHOW_DIRECTIVE = f'#show {IN_SYMBOL}/1.'


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
    simple_constraints_code, complex_constraints_code = __generate_constraints_code(model, root_name)
    instances_code, instances_dictionary = __generate_instances_code(model, root_name)

    return f'{info} \n{root_code}' \
           f'\n%\n% Hierarchy ontology definitions\n%\n{hierarchy_def}\n%\n% Component hierarchy\n%\n{hierarchy_code}' \
           f'\n%\n% Associations ontology definitions\n%\n{associations_def}\n%\n% Associations\n%\n{associations_code}' \
           f'\n%\n% Resources ontology definitions\n%\n{resource_def}\n%\n% Resource\n%\n{resource_code}' \
           f'\n%\n% Ports ontology definitions\n%\n{ports_def}\n%\n% Ports\n%\n{ports_code}' \
           f'\n%\n% Constraints\n%\n%\n% Simple constraints\n%\n{simple_constraints_code}' \
           f'\n%\n% Complex constraints\n%\n{complex_constraints_code}' \
           f'\n%\n% Instances\n%\n{instances_code}' \
           f'\n\n{SHOW_DIRECTIVE}', instances_dictionary


def __generate_code_info():
    return f'%\n% THIS CODE IS AUTOMATICALLY GENERATED\n%\n'


def __generate_root_code(root_name: str) -> str:
    root_code = ''
    root_code += f'{ROOT_SYMBOL}({CMP_VARIABLE}) :- {root_name}({CMP_VARIABLE}).\n'
    root_code += f'{CMP_SYMBOL}({CMP_VARIABLE}) :- {root_name}({CMP_VARIABLE}).\n'
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
    definitions += f':- {CMP_SYMBOL}({CMP_VARIABLE}2), 2 {{ {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, {N_VARIABLE}) : {CMP_SYMBOL}({CMP_VARIABLE}1), {PAN_SYMBOL}({N_VARIABLE}) }}.\n'
    definitions += f'{PPAT_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2) :- {PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, _).\n'
    definitions += f'{PPAT_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}3) :- {PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, _), {CMP_SYMBOL}({CMP_VARIABLE}3), {PPAT_SYMBOL}({CMP_VARIABLE}2, {CMP_VARIABLE}3).\n'
    definitions += f':- {PPAT_SYMBOL}({CMP_VARIABLE}, {CMP_VARIABLE}), {CMP_SYMBOL}({CMP_VARIABLE}).\n'
    return definitions


def __generate_associations_code(model: Model, root_name: str) -> str:
    associations_code = ''
    for c in model.hierarchy:
        if c.association:
            associations_code += f'{PAN_SYMBOL}("{c.name}").\n'
            associations_code += f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") :- ' \
                                 f'{root_name}({CMP_VARIABLE}1), {c.name}({CMP_VARIABLE}2).\n'
            min_ = '' if not c.association.min_ else c.association.min_
            max_ = '' if not c.association.max_ else c.association.max_
            associations_code += f'{min_} {{ {PA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") : ' \
                                 f'{PPA_SYMBOL}({CMP_VARIABLE}1, {CMP_VARIABLE}2, "{c.name}") }} {max_} :- ' \
                                 f'{IN_SYMBOL}({CMP_VARIABLE}1), {root_name}({CMP_VARIABLE}1).\n'
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
                prt_code += f'{PRT_SYMBOL}({PRT_VARIABLE}) :- {prt.name}({PRT_VARIABLE}).\n'
                # Compatibility
                for compatible_with_id in prt.compatible_with:
                    prt2 = model.get_port_by_id(compatible_with_id)
                    prt_code += f'{CMB_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) :- ' \
                                f'{prt.name}({PRT_VARIABLE}1), {prt2.name}({PRT_VARIABLE}2).\n'
                prt_individual_names = __get_port_individual_names(c, prt)
                for prt_individual_name in prt_individual_names:
                    prt_code += f'{PON_SYMBOL}("{prt_individual_name}").\n'
                    # prt_code += f'{PRT_SYMBOL}({PRT_VARIABLE}) :- {prt_individual_name}({PRT_VARIABLE}).\n'
                    # Compatibility
                    # for compatible_with_id in prt.compatible_with:
                    #     prt2 = model.get_port_by_id(compatible_with_id)
                    #     for c2 in model.hierarchy:
                    #         if compatible_with_id in c2.ports:
                    #             prt_individual_names_2 = __get_port_individual_names(c2, prt2)
                    #             for prt_individual_name_2 in prt_individual_names_2:
                    #                 prt_code += f'{CMB_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) :- ' \
                    #                             f'{prt_individual_name}({PRT_VARIABLE}1), {prt_individual_name_2}({PRT_VARIABLE}2). \n'
                    # Port on device
                    prt_code += f'1 {{ {PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}, "{prt_individual_name}") : ' \
                                f'{prt.name}({PRT_VARIABLE}) }} 1 :- ' \
                                f'{IN_SYMBOL}({CMP_VARIABLE}), {c.name}({CMP_VARIABLE}).\n'
                    # Force connection
                    if prt.force_connection:
                        prt_code += f':- {c.name}({CMP_VARIABLE}), {prt.name}({PRT_VARIABLE}1), ' \
                                    f'{PO_SYMBOL}({CMP_VARIABLE}, {PRT_VARIABLE}1, "{prt_individual_name}"), ' \
                                    f'{{{CN_SYMBOL}({PRT_VARIABLE}1, {PRT_VARIABLE}2) : {PRT_SYMBOL}({PRT_VARIABLE}2)}} 0.\n'
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
            ctr_code += '\n' # Do not put the ';' sign after last part
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


def __generate_simple_constraints_code(model: Model, root_name: str) -> str:
    ctrs_code = ''
    for ctr in model.simple_constraints:
        partial_ctr_code = __generate_simple_constraint_distinct_partial_code(ctr, model) if ctr.distinct \
            else __generate_simple_constraint_partial_code(ctr, model)
        ctrs_code += f':- {root_name}({CMP_VARIABLE}1), {DEFAULT_NEGATION_SYMBOL} {partial_ctr_code}.\n'
    return ctrs_code


def __generate_implication_part(conditions: List[SimpleConstraint], model: Model, root_name: str) -> Tuple[str, List[str]]:
    heads = []
    code = ''
    for condition in conditions:
        condition_code = __generate_simple_constraint_distinct_partial_code(condition, model) \
            if condition.distinct else __generate_simple_constraint_partial_code(condition, model)
        head = condition.name.replace(' ', '_')  # when using names, make sure they don't contain space # TODO: do this to others as well
        code += f'{head} :- {root_name}({CMP_VARIABLE}1), {condition_code}.\n'
        heads.append(head)
    return code, heads


def __generate_implication_complete_part(head: str, names: List[str], all_: bool) -> str:
    body = f"{', '.join(names)}" if all_ else f"1 {{ {'; '.join(names)} }}"
    return f'{head} :- {body}.\n'


def __generate_complex_constraints_code(model: Model, root_name: str) -> str:
    ctrs_code = ''
    for ctr in model.complex_constraints:
        antecedents_code, antecedents_heads = __generate_implication_part(ctr.antecedent, model, root_name)
        consequents_code, consequents_heads = __generate_implication_part(ctr.consequent, model, root_name)
        antecedent_head = f'{ctr.name.replace(" ", "_")}_antecedent'
        antecedent_complete_code = __generate_implication_complete_part(antecedent_head, antecedents_heads, ctr.antecedent_all)
        consequent_head = f'{ctr.name.replace(" ", "_")}_consequent'
        consequent_complete_code = __generate_implication_complete_part(consequent_head, consequents_heads, ctr.consequent_all)
        complete_implication = f':- {antecedent_head}, {DEFAULT_NEGATION_SYMBOL} {consequent_head}.\n'
        ctrs_code += f'{antecedents_code}\n' \
                     f'{consequents_code}\n' \
                     f'{antecedent_complete_code}' \
                     f'\n{consequent_complete_code}' \
                     f'\n{complete_implication}'
    return ctrs_code


def __generate_constraints_code(model: Model, root_name: str) -> Tuple[str, str]:
    # Simple constraints
    simple_constraints_code = __generate_simple_constraints_code(model, root_name)
    complex_constraints_code = __generate_complex_constraints_code(model, root_name)
    return simple_constraints_code, complex_constraints_code


def __generate_instances_with_symmetry_breaking(name: str, count: int, offset: int) -> str:
    instance_code = f'{name}Domain({offset+1}..{offset+count}).\n'
    instance_code += f'0 {{{name}({INSTANCE_VARIABLE}) : {name}Domain({INSTANCE_VARIABLE})}} {count}.\n'
    instance_code += f'{name}({INSTANCE_VARIABLE}1) :- {name}Domain({INSTANCE_VARIABLE}1), ' \
                     f'{name}Domain({INSTANCE_VARIABLE}2), {name}({INSTANCE_VARIABLE}2), ' \
                     f'{INSTANCE_VARIABLE}1 < {INSTANCE_VARIABLE}2.\n'
    return instance_code


def __generate_instances_code(model: Model, root_name: str) -> str:
    inst_code = ''
    inst_code += f'{root_name}(0..0).\t% ROOT\n\n'
    offset = 0
    for cmp in model.get_leaf_components():
        if cmp.count:
            cmp_instance_code = __generate_instances_with_symmetry_breaking(cmp.name, cmp.count, offset) if cmp.symmetry_breaking \
                else f'{cmp.name}({offset+1}..{offset+cmp.count}).\n'
            inst_code += cmp_instance_code
            offset += cmp.count
        for prt_id, prt_count in cmp.ports.items():
            ports_count = cmp.count * prt_count
            prt = model.get_port_by_id(prt_id)
            prt_instance_code = __generate_instances_with_symmetry_breaking(prt.name, ports_count, offset) if cmp.symmetry_breaking \
                else f'{prt.name}({offset+1}..{offset+ports_count}).\n'
            offset += ports_count
            inst_code += prt_instance_code
        inst_code += '\n'
    return inst_code




















