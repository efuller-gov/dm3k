"""
GENERAL NOTES FOR ALL "<opt>_commands.py"  FILES...
   Needs to include all extensions of Command/UndoableCommand available for this specific optimizer

   Make sure this module declares what command are possible -> COMMAND_CLASS_MAP (at the end).
      the Keys of the COMMAND_CLASS_MAP are the names of the commands in the "cmd_dict"
"""
import copy
import inspect
import logging
import re
import sys

from dm3k.slim_optimizer.util.command_pattern import UndoableCommand

log = logging.getLogger(__name__)


class FullHouseCommand(UndoableCommand):
    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {}
        self._undo_cmd_dict = {}
        self._cmd_str = ""

    def __str__(self):
        return self._cmd_str

    def execute(self):
        self._receiver.modify(self._cmd_dict, self._timestamp)

    def undo(self):
        self._receiver.modify(self._undo_cmd_dict, self._timestamp)


class ForceChildActivityCommand(FullHouseCommand):
    """
    child activity must be selected in the solution (regardless of score)
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "force_child_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "clear_child_force", "args": args}
        self._cmd_str = "force_child_activity({0})".format(args[0])


class ForbidChildActivityCommand(FullHouseCommand):
    """
    child activity must NOT be selected in the solution (regardless of score)
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "forbid_child_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "clear_child_forbid", "args": args}
        self._cmd_str = "forbid_child_activity({0})".format(args[0])


class ClearChildForceCommand(FullHouseCommand):
    """
    Removes entry from the list of forced child activities
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._undo_cmd_dict = {"cmd": "force_child_activity", "args": args}
        self._cmd_dict = {"cmd": "clear_child_force", "args": args}
        self._cmd_str = "clear_child_force({0})".format(args[0])


class ClearChildForbidCommand(FullHouseCommand):
    """
    Removes entry from the list of forbidden child activities
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._undo_cmd_dict = {"cmd": "forbid_child_activity", "args": args}
        self._cmd_dict = {"cmd": "clear_child_forbid", "args": args}
        self._cmd_str = "clear_child_forbid({0})".format(args[0])


class RemoveFromResourceContainerCommand(FullHouseCommand):
    """
    removes a child or parent resource from a resource container
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_from_resource_container", "args": args}
        self._undo_cmd_dict = {"cmd": "return_to_resource_container", "args": args}
        self._cmd_str = "remove_from_resource_container({0})".format(args[0])


class ReturnToResourceContainerCommand(FullHouseCommand):
    """
    returns a removed child or parent resource to a resource container
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "return_to_resource_container", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_from_resource_container", "args": args}
        self._cmd_str = "return_to_resource_container({0})".format(args[0])


class RemoveFromParentActivityCommand(FullHouseCommand):
    """
    removes a child activity from a parent activity
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_from_parent_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "return_to_parent_activity", "args": args}
        self._cmd_str = "remove_from_parent_activity({0})".format(args[0])


class ReturnToParentActivityCommand(FullHouseCommand):
    """
    returns a removed child activity to a parent activity
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "return_to_parent_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_from_parent_activity", "args": args}
        self._cmd_str = "return_to_parent_activity({0})".format(args[0])


class ModifyParentBudgetCommand(FullHouseCommand):
    """
    modifies the budget of a parent resource
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)
        undo_args = args.copy()
        if args[1] in receiver.to_data()["avail_parent_amt"]:
            undo_args[0] = receiver.to_data()["avail_parent_amt"][args[1]]
        else:
            undo_args[0] = 0

        self._cmd_dict = {"cmd": "modify_parent_budget", "args": args}
        self._undo_cmd_dict = {"cmd": "modify_parent_budget", "args": undo_args}
        self._cmd_str = "modify_parent_budget({0})".format(args[0])


class ModifyChildBudgetCommand(FullHouseCommand):
    """
    modifies the budget of a child resource
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)
        undo_args = args.copy()
        if args[1] in receiver.to_data()["avail_child_amt"]:
            undo_args[0] = receiver.to_data()["avail_child_amt"][args[1]]
        else:
            undo_args[0] = 0

        self._cmd_dict = {"cmd": "modify_child_budget", "args": args}
        self._undo_cmd_dict = {"cmd": "modify_child_budget", "args": undo_args}
        self._cmd_str = "modify_child_budget({0})".format(args[0])


class ModifyParentCostCommand(FullHouseCommand):
    """
    modifies the cost of a parent activity
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)
        undo_args = args.copy()
        if (args[1], args[2]) in receiver.to_data()["req_parent_amt"]:
            undo_args[0] = receiver.to_data()["req_parent_amt"][(args[1], args[2])]
        else:
            undo_args[0] = 0

        self._cmd_dict = {"cmd": "modify_parent_cost", "args": args}
        self._undo_cmd_dict = {"cmd": "modify_parent_cost", "args": undo_args}
        self._cmd_str = "modify_parent_cost({0})".format(args[0])


class ModifyChildCostCommand(FullHouseCommand):
    """
    modifies the cost of a child activity
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)
        undo_args = args.copy()
        if (args[1], args[2]) in receiver.to_data()["req_child_amt"]:
            undo_args[0] = receiver.to_data()["req_child_amt"][(args[1], args[2])]
        else:
            undo_args[0] = 0

        self._cmd_dict = {"cmd": "modify_child_cost", "args": args}
        self._undo_cmd_dict = {"cmd": "modify_child_cost", "args": undo_args}
        self._cmd_str = "modify_child_cost({0})".format(args[0])


class AddChildAllocationCommand(FullHouseCommand):
    """
    enables a child resource to be allocated to a child activity (adds the possibility)
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_child_allocation", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_child_allocation", "args": args}
        self._cmd_str = "add_child_allocation({0})".format(args[0])


class RemoveChildAllocationCommand(FullHouseCommand):
    """
    disables a child resource from being allocated to a child activity (removes the possibility)
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_child_allocation", "args": args}
        self._undo_cmd_dict = {"cmd": "add_child_allocation", "args": args}
        self._cmd_str = "remove_child_allocation({0})".format(args[0])


class AddParentAllocationCommand(FullHouseCommand):
    """
    enables a parent resource to be allocated to a parent activity (adds the possibility)
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_parent_allocation", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_parent_allocation", "args": args}
        self._cmd_str = "add_parent_allocation({0})".format(args[0])


class RemoveParentAllocationCommand(FullHouseCommand):
    """
    disables a parent resource from being allocated to a parent activity (removes the possibility)
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_parent_allocation", "args": args}
        self._undo_cmd_dict = {"cmd": "add_parent_allocation", "args": args}
        self._cmd_str = "remove_parent_allocation({0})".format(args[0])


class AddNewResourceContainerCommand(FullHouseCommand):
    """
    adds a new resource container to the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_new_resource_container", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_resource_container", "args": args}
        self._cmd_str = "add_new_resource_container({0})".format(args[0])


class RemoveResourceContainerCommand(FullHouseCommand):
    """
    remove resource container from the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_resource_container", "args": args}
        self._undo_cmd_dict = {"cmd": "add_new_resource_container", "args": args}
        self._cmd_str = "remove_resource_container({0})".format(args[0])


class AddNewParentResourceCommand(FullHouseCommand):
    """
    adds a new parent resource to the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_new_parent_resource", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_parent_resource", "args": args}
        self._cmd_str = "add_new_parent_resource({0})".format(args[0])


class RemoveParentResourceCommand(FullHouseCommand):
    """
    remove parent resource from the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_parent_resource", "args": args}
        self._undo_cmd_dict = {"cmd": "add_new_parent_resource", "args": args}
        self._cmd_str = "remove_parent_resource({0})".format(args[0])


class AddNewChildResourceCommand(FullHouseCommand):
    """
    adds a new child resource to the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_new_child_resource", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_child_resource", "args": args}
        self._cmd_str = "add_new_child_resource({0})".format(args[0])


class RemoveChildResourceCommand(FullHouseCommand):
    """
    remove child resource from the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_child_resource", "args": args}
        self._undo_cmd_dict = {"cmd": "add_new_child_resource", "args": args}
        self._cmd_str = "remove_child_resource({0})".format(args[0])


class AddNewParentActivityCommand(FullHouseCommand):
    """
    adds a new parent activity to the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_new_parent_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_parent_activity", "args": args}
        self._cmd_str = "add_new_parent_activity({0})".format(args[0])


class RemoveParentActivityCommand(FullHouseCommand):
    """
    remove parent activity from the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_parent_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "add_new_parent_activity", "args": args}
        self._cmd_str = "remove_parent_activity({0})".format(args[0])


class AddNewChildActivityCommand(FullHouseCommand):
    """
    adds a new child activity to the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "add_new_child_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "remove_child_activity", "args": args}
        self._cmd_str = "add_new_child_activity({0})".format(args[0])


class RemoveChildActivityCommand(FullHouseCommand):
    """
    remove child activity from the problem
    """

    def __init__(self, receiver, args):
        super().__init__(receiver, args)

        self._cmd_dict = {"cmd": "remove_child_activity", "args": args}
        self._undo_cmd_dict = {"cmd": "add_new_child_activity", "args": args}
        self._cmd_str = "remove_child_activity({0})".format(args[0])


class ModifyPrioritiesCommand(UndoableCommand):
    def __init__(self, receiver, args):
        super().__init__(receiver, args)
        self._slim_manager = self._args[1]
        self._old_priorities = copy.deepcopy(self._slim_manager.get_priority_manager().get_priorities_dict())

    def __str__(self):
        return "modify_priorities(...)"

    def execute(self):
        self._slim_manager.set_priorities(self._args[0], self._args[2])

    def undo(self):
        self._slim_manager.set_priorities(self._old_priorities, self._args[2])


COMMAND_CLASS_MAP = {}
# This loop will take all the classes defined in this file and create the desired mapping
#   e.g. {"add_new_child_resource" : AddNewChildResourceCommand}
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        # Converts the CamelCase name to a snake_case name with Command removed
        command_map_key = "_".join(re.findall("[A-Z][^A-Z]*", obj.__name__)).lower().split("_command")[0]
        COMMAND_CLASS_MAP[command_map_key] = obj
