#! /usr/bin/env python3


from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import build_model
import pddl_to_prolog
import pddl
import timers

def get_fluent_facts(task, model):
    fluent_predicates = set()
    for action in task.actions:
        for effect in action.effects:
            fluent_predicates.add(effect.literal.predicate)
    for axiom in task.axioms:
        fluent_predicates.add(axiom.name)
    return {fact for fact in model
            if fact.predicate in fluent_predicates}

def get_objects_by_type(typed_objects, types):
    result = defaultdict(list)
    supertypes = {}
    for type in types:
        supertypes[type.name] = type.supertype_names
    for obj in typed_objects:
        result[obj.type_name].append(obj.name)
        for type in supertypes[obj.type_name]:
            result[type].append(obj.name)
    return result

def instantiate_goal(goal, init_facts, fluent_facts):
    # With the way this module is designed, we need to "instantiate"
    # the goal to make sure we properly deal with static conditions,
    # in particular flagging unreachable negative static goals as
    # impossible. See issue1055.
    #
    # This returns None for goals that are impossible due to static
    # facts.

    # HACK! The implementation of this probably belongs into
    # pddl.condition or a similar file, not here. The `instantiate`
    # method of conditions with its slightly weird interface and the
    # existence of the `Impossible` exceptions should perhaps be
    # implementation details of `pddl`.
    result = []
    try:
        goal.instantiate({}, init_facts, fluent_facts, result)
    except pddl.conditions.Impossible:
        return None
    return result

# The input task must have been normalized
# The model has been computed by build_model.compute_model
def instantiate(task: pddl.Task, model: Any) -> Tuple[
             bool, # relaxed_reachable
             Set[pddl.Literal], # fluent_facts (ground)
             List[pddl.PropositionalAction], # instantiated_actions
             Optional[List[pddl.Literal]], # instantiated_goal
             List[pddl.PropositionalAxiom], # instantiated_axioms
             Dict[pddl.Action, List[str]] # reachable_action_parameters
            ]:
    relaxed_reachable = False
    fluent_facts = get_fluent_facts(task, model)
    init_facts = set()
    init_assignments = {}
    for element in task.init:
        if isinstance(element, pddl.Assign):
            init_assignments[element.fluent] = element.expression
        else:
            init_facts.add(element)

    type_to_objects = get_objects_by_type(task.objects, task.types)

    instantiated_actions = []
    instantiated_axioms = []
    reachable_action_parameters = defaultdict(list)
    for atom in model:
        if isinstance(atom.predicate, pddl.Action):
            action = atom.predicate
            parameters = action.parameters
            inst_parameters = atom.args[:len(parameters)]
            # Note: It's important that we use the action object
            # itself as the key in reachable_action_parameters (rather
            # than action.name) since we can have multiple different
            # actions with the same name after normalization, and we
            # want to distinguish their instantiations.
            reachable_action_parameters[action].append(inst_parameters)
            variable_mapping = {par.name: arg
                                for par, arg in zip(parameters, atom.args)}
            inst_action = action.instantiate(
                variable_mapping, init_facts, init_assignments,
                fluent_facts, type_to_objects,
                task.use_min_cost_metric)
            if inst_action:
                instantiated_actions.append(inst_action)
        elif isinstance(atom.predicate, pddl.Axiom):
            axiom = atom.predicate
            variable_mapping = {par.name: arg
                                for par, arg in zip(axiom.parameters, atom.args)}
            inst_axiom = axiom.instantiate(variable_mapping, init_facts, fluent_facts)
            if inst_axiom:
                instantiated_axioms.append(inst_axiom)
        elif atom.predicate == "@goal-reachable":
            relaxed_reachable = True

    instantiated_goal = instantiate_goal(task.goal, init_facts, fluent_facts)

    return (relaxed_reachable, fluent_facts,
            instantiated_actions, instantiated_goal,
            sorted(instantiated_axioms), reachable_action_parameters)


def explore(task):
    prog = pddl_to_prolog.translate(task)
    model = build_model.compute_model(prog)
    with timers.timing("Completing instantiation"):
        return instantiate(task, model)


def instantiate_rule(initial_facts, variable_mapping, conditions, effect, model, variables_values, atoms):
    if not conditions:
        if model[effect.predicate]:
            ground_operators = []
            for atom in model[effect.predicate]:
                if atom.predicate.startswith("p$") or (atom.predicate in variables_values and str(atom) in variables_values[atom.predicate]):
                    effect_is_mapped = True
                    for i in range(len(effect.args)):
                        if effect.args[i][0] == "?":
                            if effect.args[i] in variable_mapping:
                                if variable_mapping[effect.args[i]] != atom.args[i]:
                                    effect_is_mapped = False
                                    break
                        else:
                            if effect.args[i] != atom.args[i]:
                                effect_is_mapped = False
                                break
                    if effect_is_mapped:
                        ground_operators.append((atom, atoms))
            return ground_operators
        return []
    
    current_condition = conditions[0]
    if model[current_condition.predicate]:
        result = []
        for atom in model[current_condition.predicate]:
            var_mapping = variable_mapping.copy()
            is_mapped = True
            for i in range(len(current_condition.args)):
                if current_condition.args[i][0] == "?":
                    if current_condition.args[i] in var_mapping:
                        if var_mapping[current_condition.args[i]] != atom.args[i]:
                            is_mapped = False
                            break
                    else:
                        var_mapping[current_condition.args[i]] = atom.args[i]
                else:
                    if current_condition.args[i] != atom.args[i]:
                        is_mapped = False
                        break
            if is_mapped:
                r = None
                if "@" not in atom.predicate and (atom.predicate.startswith("p$") or (atom.predicate in variables_values and str(atom) in variables_values[atom.predicate])):
                    r = instantiate_rule(initial_facts, var_mapping, conditions[1:], effect, model, variables_values, atoms + [atom])
                elif initial_facts[atom.predicate] and atom not in initial_facts[atom.predicate]:
                    continue
                else:
                    r = instantiate_rule(initial_facts, var_mapping, conditions[1:], effect, model, variables_values, atoms)
                if r:
                    result = result + r
        return result
    return []

def instantiate_for_relaxation_heuristic(prog: pddl_to_prolog.PrologProgram, model: Any, variables_values, initial_facts):
    ground_operators = []
    model_with_predicates = defaultdict(list)
    initial_facts_with_predicates = defaultdict(list)
    with timers.timing("Building dictionary for model with predicates"):
        for atom in model:
            model_with_predicates[atom.predicate].append(atom)
    with timers.timing("Building dictionary for facts of initial state with predicates"):
        for atom in initial_facts:
            if isinstance(atom, pddl.Atom):
                initial_facts_with_predicates[atom.predicate].append(atom)
    with timers.timing("Completing instantiation of rules"):
        for rule in prog.rules:
            if "@goal-reachable" in rule.effect.predicate:
                continue
            result = instantiate_rule(initial_facts_with_predicates, variable_mapping={}, conditions=rule.conditions,
                                effect=rule.effect, model=model_with_predicates, variables_values=variables_values, atoms=[])
            if result:
                for effect, conditions in result:
                    ground_operators.append((effect, tuple(conditions), rule.weight))
    return set(ground_operators)

def compute_operators_for_relaxation_heuristic(task: pddl.Task, sas_task):
    with timers.timing("Building rules"):
        prog = pddl_to_prolog.translate_optimize(task)
    model = build_model.compute_model(prog)

    variables_values = defaultdict(list)
    for values in sas_task.variables.value_names:
        for value in values:
            if "NegatedAtom" not in value:
                variables_values[value.split()[1].split("(")[0]].append(value)
    ground_operators = instantiate_for_relaxation_heuristic(prog, model, variables_values, task.init)
    with timers.timing("Writing operators to output file"):
        with open("operators_relaxation_heuristic.txt", "w") as output_file:
            output(ground_operators, output_file)

def output(operators, output_file):
    for operator in operators:
        print(operator[0], file=output_file)
        for precondition in operator[1]:
            print(precondition, file=output_file)
        print("cost", file=output_file)
        print(operator[2], file=output_file)
    print("end_operators", file=output_file)

if __name__ == "__main__":
    import pddl_parser
    task = pddl_parser.open()
    relaxed_reachable, atoms, actions, goals, axioms, _ = explore(task)
    print("goal relaxed reachable: %s" % relaxed_reachable)
    print("%d atoms:" % len(atoms))
    for atom in atoms:
        print(" ", atom)
    print()
    print("%d actions:" % len(actions))
    for action in actions:
        action.dump()
        print()
    print("%d axioms:" % len(axioms))
    for axiom in axioms:
        axiom.dump()
        print()
    print()
    if goals is None:
        print("impossible goal")
    else:
        print("%d goals:" % len(goals))
        for literal in goals:
            literal.dump()
