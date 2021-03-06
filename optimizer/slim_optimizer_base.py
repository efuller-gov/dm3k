"""
The base optimizer class attempts to make it easy to create new optimizers, which only
requires filling in certain pieces: particularly the *model*, *input*, and *output*
classes.
"""
from __future__ import annotations  # needed for the self-referential type hints

import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd
import psutil  # See https://github.com/PyUtilib/pyutilib/issues/31  - getting ValueError: signal only works in main thread
import pyutilib.subprocess.GlobalData
from pyomo.common.tempfiles import TempfileManager
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from pyutilib.common._exceptions import ApplicationError

from optimizer.util.history_pattern import HistoryManager
from optimizer.util.util import remove_old_temp_files

pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False

log = logging.getLogger(__name__)

# set up logging
app_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
LOG_DIR = os.path.join(app_directory, "logs")
if not os.path.exists(LOG_DIR):
    log.debug("Creating LOG_DIR=" + str(LOG_DIR))
    os.makedirs(LOG_DIR)


class OptimizerBase(ABC):
    def __init__(self, input_class: InputBase, model_class: ModelBase, output_class: OutputBase):
        """
        Create the Optimizer itself.

            NOTE - individual optimizers should extend this class in order to specify the corresponding inputs

        Args:
            input_class: python class that extends class InputBase below
            model_class: python class that extends class ModelBase below OR
                a list of python classes that extends class ModelBase below.
                **NOTE** *- the list of model_classes is used when the user wants to
                provide multiple possible ways to solve the problem.  The
                model_classes are considered in order in the list.  If a
                model_class can solve the problem described by the input (see
                ModelBase.can_solve method), the model_class is used.  If not
                the next model_class is checked...until a model_class is found
                that solves the problem or all model_classes provided fail the
                checks.*
            output_class: python class that extends class OutputBase below

        """
        self._model_class = model_class
        self._output_class = output_class

        self._hist_mgr = HistoryManager()  # enables system to generate timings and memory usage

        self._input_instance = None
        self._constraints_dataset = ""
        self._input = input_class()
        self._model = None
        self._output = None

    def ingest(self, input_dict: dict):
        """
        Ingest a new input dataset

        NOTE - ingest effectively clears the class (model=None, output=None) to avoid weird states when user ingests
               and asks for output prior to solving

        :param dict input_dict: a dict containing the name of the input and the files associated with this input
        :return list validation_errors: a list of errors where each error is a dict with the following attributes...
                    "err_code" : <a int where int is key in VALIDATE_ERROR_CODE>,
                    "err_txt" : <human readable text that describes the error
                    "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,
                    "fix": <string name of process performed to fix the error  or None>,
                    "is_fatal_error": <boolean; True = error is fatal, False = error is fixable>

        :raises ValueError: if a fatal error is found in the input (such that the system cannot fix the issue).

                NOTE - when catching this error (i.e. except ValueError as e:),
                    e.args[1] = text of error = "Input Data Failed Validation"
                    e.args[0] = list of validation errors...at least one of these caused the fatal error
        """
        self._hist_mgr.start_tag("Ingest from input dictionary")
        fatal, validation_errors = self._input.ingest_validate(input_dict)
        if fatal:
            raise ValueError(validation_errors, "Input Data Failed Validation")

        self._model = None
        self._output = None
        self._hist_mgr.end_tag("Ingest from input dictionary")

        return validation_errors

    def build(self):
        """
        Build a new Optimizer Model

        :return: None
        """
        data = self._input.to_data()
        if not data:
            log.error("You are attempting to build a model before ingesting data...you must do ingest method first")
            raise UnboundLocalError("You must ingest data prior to building the model")

        self._hist_mgr.start_tag("Finding Model to use")
        if isinstance(self._model_class, list):
            for mc in self._model_class:
                self._model = mc()
                if self._model.can_solve(self._input):
                    break
        else:
            self._model = self._model_class()

        log.debug(f"Building with Class: {self._model.__class__.__name__}")
        self._hist_mgr.end_tag("Finding Model to use")

        self._hist_mgr.start_tag("Building Model")
        self._model.build(data)
        self._hist_mgr.end_tag("Building Model")

    def solve(self, solver="glpk", tee=False, timeout=None, retries=3, mipgap=None, keepfiles=True):
        """
        Solve the optimizer Model and gather input into the output class

        :param str solver: Only one solver currently available ("glpk")
        :param bool tee: Is pyomo logging to the terminal enabled
        :param int timeout: By default there is no timeout
        :param int retries: Number of max attempts at running the solver
        :param float mipgap: Tolerance for solver
        :param bool keepfiles: Set to true if pyomo files should be kept
        :return: None
        """

        if self._model is None:
            log.warning("You are attempting to solve the model before building it...will attempt to build model for you")
            # instead of throwing error here, just build it for them if they did steps out of order
            self.build()

        self._hist_mgr.start_tag("Solving Model")
        self._model.solve(
            solver=solver,
            tee=tee,
            timeout=timeout,
            retries=retries,
            mipgap=mipgap,
            keepfiles=keepfiles,
            constraints_dataset=self._constraints_dataset,
        )
        self._hist_mgr.end_tag("Solving Model")

        self._hist_mgr.start_tag("Gathering Output")
        self._output = self._model.fill_output(self._output_class)
        self._hist_mgr.end_tag("Gathering Output")

    def get_results(self) -> dict:
        """
        Return the results from the last solve step

        :return dict output_dict: a dictionary containing the output of the modeling
        """
        if self._output is None:
            log.warning("You must ingest, build the model, and solve it prior to getting output...will attempt to solve for you")
            # instead of throwing error here, just attempt to solve model for them if they did steps out of order
            self.solve()

        return self._output.result

    @property
    def output(self):
        return self._output

    def get_history_df(self) -> pd.DataFrame:
        """
        Get the history of operations and metrics on their runtime and memory usage.  This can be used to test the performance of optimizers.

        :return pandas.DataFrame history_df: pandas DataFrame with information about runtime and memory events
        """
        return pd.DataFrame(
            self._hist_mgr.get_history(), columns=["datetime", "operation", "time_to_run_sec", "memory_gain_MB", "end_memory_MB"]
        )


class InputBase(ABC):
    def __init__(self):

        # this attribute needs to be a dict that can be dumped by json.dump
        self._data = {}

    @abstractmethod
    def ingest_validate(self, input_dict: dict):
        """
        Validate the constraints and activity scores to determine if following Errors are found

        ERROR_CODE DESCRIPTIONS
            1. the necessary constraints files do not exist
            2. the formats of the constraints files are incorrect
            3. the data within the constraints files are not consistent with each other
            4. the data within the constraints files and the activity names are not consistent

        And then Load the files in the constraints path into this input (capturing them in the self._data attribute)

        :param dict input_dict: a dict containing the name of the input and the data from files associated with this input
        :return bool fatal: True=a fatal error has been found, the optimizer should not continue
        :return dict validation_errors: a list of errors where each error is a dict with the following attributes...
                    "err_code" : <a int where int is key in VALIDATE_ERROR_CODE>,
                    "err_txt" : <human readable text that describes the error>,
                    "offender" : <string or list of name(s) (of DU, resource, or resource group) that is causing error>,
                    "fix": <string name of process performed to fix the error  or None>,
                    "is_fatal_error": <boolean; True = error is fatal, False = error is fixable>
        """

    def get_info(self, info_name: str):
        """
        Returns a given field of the input dictionary

        :param str info_name: Name of particular input field that is wanted
        :return: One field from _data dictionary
        """
        return self._data.get(info_name)

    def list_info_avail(self):
        """
        Returns all keys in the input dictionary

        :return list:
        """
        return list(self._data.keys())

    def to_data(self) -> dict:
        """
        Whatever data format the model needs

        :return dict data: a dictionary containing all necessary data for the model (this will be defined on a model by model
                     basis)
        """
        return self._data


class ModelBase(ABC):
    """
    The ModelBase serves as a template for the meat of new optimizers.  These will typically extend the base class and
    build a new pyomo model using input constraints.  One must identify how to turn the input constraints into appropriate
    pyomo constraints.
    """

    def __init__(self):
        self._model = None
        self._continue_check_status = False
        self._pyomo_log_name = None
        self._max_solve_no_update = 600
        self.kill_glpsol_if_stuck = False
        self.new_timeout = None

    @abstractmethod
    def can_solve(self, input_instance) -> bool:
        """
        In the event the system can leverage multiple models, this function is used to determine if this model
        can solve the input.

        :param input_instance: a instance of the InputBase class
        :return: Boolean, True = yes, this model can solve it.  False = something about input cannot be solved by model
        """

    @abstractmethod
    def build(self, data):
        """
        Build the pyomo model in self._model

        :param data: a dictionary containing all necessary data for the model (this will be defined on a model by model
                     basis)
        :return: None
        """

    def solve(self, solver="glpk", tee=False, timeout=None, retries=3, mipgap=None, constraints_dataset="unknown", keepfiles=True):
        """
        Solve the self._model using the solver

        NOTE - currently only glpk has been tested (may add cplex, gurobi)

        :param str solver: Only one solver currently available ("glpk")
        :param bool tee: Is pyomo logging to the terminal enabled
        :param int timeout: By default there is no timeout
        :param int retries: Number of max attempts at running the solver
        :param float mipgap: Tolerance for solver
        :param str constraints_dataset: Name of dataset where there are constraints
        :param bool keepfiles: Set to true if pyomo files should be kept
        :return: None
        """
        temp_dir_name = "/tmp/solver"
        TempfileManager.tempdir = temp_dir_name
        if not os.path.isdir(temp_dir_name):
            os.mkdir(temp_dir_name)
        remove_old_temp_files(temp_dir_name)

        log_name = "pyomo_" + str(type(self).__name__) + ".log"
        results_name = "pyomo_results_" + str(type(self).__name__) + ".log"

        # solve the model
        log.info("Running Solver...")
        opt = SolverFactory(solver)
        if solver == "glpk" and mipgap:
            opt.options["mipgap"] = mipgap

        i = 1
        results = None
        opt_log_dir = None
        while i <= retries:
            log.info("Attempt %s/%s to complete solver", i, retries)
            try:
                opt_log_dir = os.path.join(LOG_DIR, "pyomo_logs", constraints_dataset + "_" + datetime.now().isoformat())
                os.makedirs(opt_log_dir)
                self._pyomo_log_name = os.path.join(opt_log_dir, log_name)

                if solver == "glpk":
                    opt.options["log"] = self._pyomo_log_name
                    if self.new_timeout:
                        opt.options["tmlim"] = self.new_timeout
                    elif timeout:
                        opt.options["tmlim"] = timeout
                        # Do a slightly progressive timeout for each retry
                        timeout = int(timeout * 1.20)

                self._continue_check_status = True
                status_thread = threading.Thread(target=self.check_solve_status)
                status_thread.start()

                # There will still be three "Solver .. file" lines displayed on the console due to the use of keepfiles
                results = opt.solve(self._model, tee=tee, keepfiles=keepfiles)
                self._continue_check_status = False

                status = results.solver.status
                termination_condition = results.solver.termination_condition

                if status == SolverStatus.ok:
                    log.info("Solver finished with a status of %s", status)
                    if termination_condition == TerminationCondition.optimal:
                        log.info("Solver finished with termination condition of %s", termination_condition)
                        break
                    elif termination_condition == TerminationCondition.feasible:
                        log.warning("Solver finished with a termination condition of %s", termination_condition)
                        break
                    else:
                        log.error("Solver finished with a termination condition of %s", termination_condition)
                else:
                    log.error("Solver finish with a status of %s", status)
                    log.error("Solver finished with termination condition of %s", termination_condition)

            except ApplicationError as e:
                self._continue_check_status = False
                log.error(str(e))
                if i == retries:
                    raise Exception("Unable to solve after %s attempts", retries).with_traceback(e.__traceback__)
            i += 1

        log.info("Done")
        # Write optimizer results
        if results and opt_log_dir:
            results.write(filename=os.path.join(opt_log_dir, results_name))

    def check_solve_status(self):
        """
        This method is called right before calling the "opt.solve" method and uses threading to monitor the status of calling that method
        """
        start_solver_time = time.time()
        best_solution = None
        seconds_find_best_solution = None
        time_of_best_solution = None
        while self._continue_check_status:
            #  Is there anything we can check?
            # self._model.objective.expr() does not have anything until solver is finished
            last_line = None
            if self._pyomo_log_name and os.path.exists(self._pyomo_log_name):
                with open(self._pyomo_log_name) as f:
                    last_line = f.readlines()[-1]
            if last_line:
                last_line_split = last_line.split()
                # Only continue to parse lines that begin with a "+"
                if last_line_split[0].startswith("+"):
                    new_best_solution = None
                    # The ">>>>>" indicates there is a new best solution
                    # There may or may not be a space after the '+'
                    if last_line_split[2] == ">>>>>":
                        new_best_solution = float(last_line_split[3])
                    elif last_line_split[1] == ">>>>>":
                        new_best_solution = float(last_line_split[2])

                    if new_best_solution:
                        # Make sure that the solution/log file actually has been updated
                        if best_solution != new_best_solution:
                            curr_time = time.time()
                            best_solution = new_best_solution
                            seconds_find_best_solution = int(curr_time - start_solver_time)
                            time_of_best_solution = curr_time
                            log.info("New best objective value is: %s", best_solution)

                if time_of_best_solution:
                    seconds_since_last_new_best_solution = time.time() - time_of_best_solution
                    if seconds_since_last_new_best_solution > self._max_solve_no_update:
                        log.warning("It has been %s seconds since last new best solution", int(seconds_since_last_new_best_solution))
                        if self.kill_glpsol_if_stuck:
                            for proc in psutil.process_iter():
                                if proc.name() == "glpsol" and proc.status() == "running":
                                    proc.kill()
                                    # fudge factor for new timeout
                                    fudge_value = max(10, int(seconds_find_best_solution * 0.1))
                                    self.new_timeout = seconds_find_best_solution + fudge_value
            if self._continue_check_status:
                time.sleep(2)

    def get_model(self):
        """
        Get the model that was built

        :return model: the pyomo model
        """
        return self._model

    @abstractmethod
    def fill_output(self, output_class) -> OutputBase:
        """
        Return the output of the model after it has been solved by instantiating an object of the output class.

        This method must interrogate the model and produce an output object.  Since models may differ,
        this method must be implemented in the subclass

        :param output_class: the OutputBase or subclass of output base
        :return output: an instance of the output_class
        """


# required output keys
VALUE_KEY = "objective_value"
ALLOC_KEY = "allocations"
TRACE_KEY = "full_trace"


class OutputBase(ABC):
    def __init__(self):
        """
        Create a new object to hold output from an optimizer solution, which is basically a dictionary of results with some convenience methods.

        """
        self._result = {}

    @property
    def result(self):
        """
        Provide the optimizer output as a python dict

        :return dict results: a dictionary of output of the optimizer solution
                                Keys must include 'objective_value', 'allocations', and 'full_trace' (additional fields can be added by each optimizer)
        """
        return self._result

    @result.setter
    def result(self, result_dict):
        self._result = result_dict

    @property
    def objective_value(self):
        """
        Provide the value of the objective function of the optimizer

        :return float objective_value: the value of the objective of the optimizer
        """
        return self._result[VALUE_KEY]

    @property
    def allocations(self):
        """
        Provide the mapping of resources to activities from the optimizer solution

        :return dict allocations: a dictionary with keys equal to resource names and values equal to lists of activities that
                             each resource is mapped to
        """
        return self._result[ALLOC_KEY]

    def get_trace_df(self, sort_results=True, ascending=False):
        """
        Return a dataframe of the "full_trace" dictionary.

        :param bool sort_results: If the DataFrame should be sorted.  Default is true
        :param bool ascending: Set to false so that the highest value is on top
        :return: the full_trace dictionary in a DataFrame format
        """
        df = pd.DataFrame(self.result[TRACE_KEY])
        df.selected = df.selected.astype(bool)
        return df.sort_values(by=["selected", "value"], ascending=ascending) if sort_results else df
