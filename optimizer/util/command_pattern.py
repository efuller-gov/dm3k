"""
Implements the command pattern that allows the server to undo multiple commands
(see https://matt.berther.io/2004/09/16/using-the-command-pattern-for-undo-functionality
"""
import logging
import time
import traceback

log = logging.getLogger(__name__)


class SuccessInfo:
    """
    Simple helper class to keep all command success info in one place

    Success Codes:


    * [0] Success
    * [-1] bad command format
    * [-2] non-existent command
    * [-3] command had no effect
    * [-4] command failed to execute (internal command failure)

    """

    def __init__(self, success, code, user_msg, internal_msg):
        """
        Create a success info object

        :param bool success: Boolean True=Success, False=Fail
        :param int code: Integer value (see Success codes above)
        :param str user_msg: a string used for external users of the system
        :param str internal_msg: a string with more detail for developers or internal users
        """
        self._success = success
        self._code = code
        self._user_msg = user_msg
        self._internal_msg = internal_msg

    def to_dict(self):
        return {"success": self._success, "code": self._code, "user_message": self._user_msg, "internal_message": self._internal_msg}


class CommandManager:
    def __init__(self):
        self._undolist = []
        self._redolist = []
        self._receiver = None
        self._cmd_map = None

    def set_receiver(self, receiver):
        self._receiver = receiver

    def set_command_map(self, cmd_map):
        self._cmd_map = cmd_map

    def get_undo_list(self):
        """

        :return: A list of string undo commands
        """
        ret = []
        for cmd in self._undolist:
            ret.append(str(cmd))
        return ret

    def get_redo_list(self):
        """

        :return: A list of string redo commands
        """
        ret = []
        for cmd in self._redolist:
            ret.append(str(cmd))
        return ret

    def clear_undo(self):
        """
        Sets _undolist to empty list
        :return: None
        """
        self._undolist = []

    def clear_redo(self):
        """
        Sets _redolist to empty list
        :return: None
        """
        self._redolist = []

    def undo(self):
        """
        Undoes the last command by removing the last entry on undo list and appending to redo list
        :return: A dict containing success information of undo command
        """
        if len(self._undolist) > 0:
            cmd = self._undolist.pop()
            self._redolist.append(cmd)
            cmd.undo()
            success_info = SuccessInfo(True, 0, "Successful undo", "Undo " + str(cmd))

        else:
            success_info = SuccessInfo(False, -3, "Nothing to Undo", "Nothing to Undo")

        return success_info.to_dict()

    def undo_all(self):
        """
        Calls undo method for each item on undo list
        :return: None
        """
        len_undo = len(self._undolist)
        if len_undo > 0:
            msg_list = []

            for x in range(len_undo):
                success_info = self.undo()
                msg_list.append(success_info["internal_message"])

            success_info = SuccessInfo(True, 0, "Successful undo", (", ".join(msg_list)))

        else:
            success_info = SuccessInfo(False, -3, "Nothing to Undo", "Nothing to Undo")

        return success_info.to_dict()

    def redo(self):
        """
        Redoes command by removing the last entry on redo list and appending to undo list
        :return: A dict containing success information of undo command
        """
        if len(self._redolist) > 0:
            cmd = self._redolist.pop()
            self._undolist.append(cmd)
            cmd.execute()

            success_info = SuccessInfo(True, 0, "Successful undo", "Redo " + str(cmd))

        else:
            success_info = SuccessInfo(False, -3, "Nothing to Redo", "Nothing to Redo")

        return success_info.to_dict()

    def is_available_cmd(self, cmd_dict):
        """
        Can this command be executed

        :param dict cmd_dict: a dict containing attributes of "cmd" (string name of the command) and "args" (list of arguments)
                              ex- {"cmd": <cmd>, "args": [<arg1>,<arg2>,...]}
        :return boolean: True = yes this command will be accepted, False = no, this command cannot be handled
        :return success_info: a dict containing indication of success, success code, user message, and internal message
        """
        if "cmd" in cmd_dict and "args" in cmd_dict:
            if cmd_dict["cmd"] in self._cmd_map:
                return True, {}
            else:
                success_info = SuccessInfo(
                    False,
                    -2,
                    "Need to supply the correct command Name",
                    "Command Name: " + str(cmd_dict["cmd"]) + " was not in COMMAND_CLASS_MAP",
                )
                return False, success_info.to_dict()
        else:
            success_info = SuccessInfo(
                False,
                -1,
                "Command format did not include cmd name or args",
                "Command: " + str(cmd_dict) + " did not include cmd or args keys",
            )
            return False, success_info.to_dict()

    # TODO what about access to undo, redo, etc from this endpoint
    def execute(self, cmd_dict):
        """
        Execute a command on the receiver

        :param dict cmd_dict: a dict containing attributes of "cmd" (string name of the command) and "args" (list of arguments)
                              ex- {"cmd": <cmd>, "args": [<arg1>,<arg2>,...]}
        :return success_info: a dict containing indication of success, success code, user message, and internal message
        """

        # check to see if it will work
        avail, success_info = self.is_available_cmd(cmd_dict)
        if not avail:
            return success_info

        # get the command
        cmd_name = cmd_dict["cmd"]
        cmd_args = cmd_dict["args"]
        cmd = self._cmd_map[cmd_name](self._receiver, cmd_args)

        # execute command
        try:
            cmd.execute()
        except Exception as e:
            log.error("Command Failed to Execute")
            log.error(e)
            log.error(traceback.format_exc())
            success_info = SuccessInfo(False, -4, "Command Failed to Execute", str(e))
            return success_info.to_dict()

        # add it to undo
        if cmd.is_undoable():
            self._undolist.append(cmd)

        success_info = SuccessInfo(True, 0, "Successful command", str(cmd))
        return success_info


class Command:
    def __init__(self, receiver, args=None):
        self._undoable = False
        self._receiver = receiver
        self._timestamp = round(time.time() * 1000)
        self._args = args

    def is_undoable(self):
        """

        :return bool: If the command is undoable or not
        """
        return self._undoable

    def __str__(self):
        # needs to return simple string form of this command (e.g. cmd(arg1, arg2))
        raise NotImplementedError("Subclasses must implement this!")

    def execute(self):
        """
        Abstract method
        """
        raise NotImplementedError("Subclasses must implement this!")


class UndoableCommand(Command):
    def __init__(self, receiver, args=None):
        super().__init__(receiver, args)
        self._undoable = True

    def undo(self):
        """
        Abstract undo method
        """
        raise NotImplementedError("Subclasses must implement this!")
