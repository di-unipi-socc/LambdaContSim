# this class represent a simpy process which runs a particular function

import simpy
from application.application import Application, ApplicationState

from application.placed_function import FunctionState, PlacedFunction
from infrastructure.node import Node
from logs import get_logger
from utils import (
    delete_executed_function,
    delete_functions_chain_by_id,
    get_next_functions_by_id,
    get_ready_functions,
    take_decision,
)
import config


class FunctionProcess:
    def __init__(
        self, fun: PlacedFunction, env: simpy.Environment, application: Application
    ):
        self.fun = fun

        self.env = env

        self.action = env.process(self.run())

        self.application = application

    def run(self):

        # get the logger
        logger = get_logger()

        # function is running
        self.fun.state = FunctionState.RUNNING

        try:

            # simulate the function execution
            yield self.env.timeout(config.sim_function_duration)

        except simpy.Interrupt:
            # function interrupted - probably there is a crash

            logger.info(
                "Application %s - Function %s has been interrupted",
                self.application.id,
                self.fun.id,
            )

            # function has been canceled
            self.fun.state = FunctionState.CANCELED

            # release resources

            fun_name = self.fun.id
            node_id = self.application.placement[fun_name].node_id
            node: Node = self.application.infrastructure_nodes[node_id]
            node.release_resources(
                self.application.placement[fun_name].memory,
                self.application.placement[fun_name].v_cpu,
            )

            return

        # function exited
        self.fun.state = FunctionState.COMPLETED

        # get functions which depends on me
        dependent_functions: list = get_next_functions_by_id(
            self.application.chain, self.fun.id
        )

        # delete myself from the chain
        delete_executed_function(self.application.chain, self.fun.id)

        # get ready functions
        ready_functions: list = get_ready_functions(self.application.chain)

        # when there aren't ready functions -> application finished
        if len(ready_functions) == 0:
            self.application.state = ApplicationState.COMPLETED

        # get ready functions which was depending on me
        to_execute: list = []
        for function in ready_functions:
            if function in dependent_functions:
                to_execute.append(function)

        # if the function is a guard of an 'if' statement
        # we have to decide which branch must be taken
        # what we know is that the guard will have 2 child in the chain
        if self.fun.is_guard:

            # probability that the guard is True, default is 0.5
            guard_probability = 0.5

            application_name = self.application.name
            guards: dict = config.applications[application_name]["guards"]

            if self.fun.id in guards.keys():
                guard_probability = guards[self.fun.id]

            # take the decision
            decision = take_decision(guard_probability)
            # print("Function %s is a guard and its value is %s (prob. of being True was %f)" % (self.fun.id, decision, guard_probability))

            taken_branch = ""
            discarded_branch = ""

            if decision:
                # take the True branch
                taken_branch = to_execute[0]
                discarded_branch = to_execute[1]
            else:
                # take the False branch
                taken_branch = to_execute[1]
                discarded_branch = to_execute[0]

            # print("taken: %s" % taken_branch)

            # delete discarded function and all functions which was depending
            deleted_functions = delete_functions_chain_by_id(
                self.application.chain, discarded_branch
            )
            # release resources
            for fun in deleted_functions:
                self.application.placement[fun].state = FunctionState.CANCELED
                node_id = self.application.placement[fun].node_id
                node: Node = self.application.infrastructure_nodes[node_id]
                node.release_resources(
                    self.application.placement[fun].memory,
                    self.application.placement[fun].v_cpu,
                )

            # execute the taken function
            fun_process = FunctionProcess(
                self.application.placement[taken_branch], self.env, self.application
            )
            self.application.function_processes[taken_branch] = fun_process

        else:
            # execute the functions
            for function_name in to_execute:
                fun_process = FunctionProcess(
                    self.application.placement[function_name],
                    self.env,
                    self.application,
                )
                self.application.function_processes[function_name] = fun_process

        # release resources

        fun_name = self.fun.id
        node_id = self.application.placement[fun_name].node_id
        node: Node = self.application.infrastructure_nodes[node_id]
        node.release_resources(
            self.application.placement[fun_name].memory,
            self.application.placement[fun_name].v_cpu,
        )
