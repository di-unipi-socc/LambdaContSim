# this class represent a simpy process which runs a particular function

import simpy
from application.application import Application, ApplicationState

from application.placed_function import FunctionState, PlacedFunction
from infrastructure.node import Node
from logs import get_logger
from utils import delete_executed_function, delete_functions_chain_by_id, get_next_functions_by_id, get_ready_functions, take_decision

class FunctionProcess:
    def __init__(self, fun : PlacedFunction, env : simpy.Environment, application : Application):
        self.fun = fun

        self.env = env

        self.action = env.process(self.run())

        self.application = application

    def run(self):

        # get the logger
        logger = get_logger()

        # function is running
        self.fun.state = FunctionState.RUNNING

        duration = 1

        try:

            yield self.env.timeout(duration)

        except simpy.Interrupt:
            logger.info("Application %s - Function %s has been interrupted", self.application.id, self.fun.id)

            # function has been canceled
            self.fun.state = FunctionState.CANCELED

            # release resources

            fun_name = self.fun.id
            node_id = self.application.placement[fun_name].node_id
            node : Node = self.application.infrastructure_nodes[node_id]
            node.release_resources(self.application.placement[fun_name].memory, self.application.placement[fun_name].v_cpu)

            return
        

        # function exited
        self.fun.state = FunctionState.COMPLETED

        #print("Function %s finished" % self.fun.id)

        # get functions which depends on me
        dependent_functions : list = get_next_functions_by_id(self.application.chain, self.fun.id)
        
        # delete myself from the chain
        delete_executed_function(self.application.chain, self.fun.id)

        # get ready functions
        ready_functions : list = get_ready_functions(self.application.chain)

        # when there aren't ready functions -> application finished
        if len(ready_functions) == 0:
            self.application.state = ApplicationState.COMPLETED

        # get ready functions which was depending on me
        to_execute : list = []
        for function in ready_functions:
            if function in dependent_functions:
                to_execute.append(function)


        # if the function is a guard of an 'if' statement
        # we have to decide which branch must be taken
        # what we know is that the guard will have 2 child in the chain
        if self.fun.is_guard:
            # take the decision with probability 0.5
            decision = take_decision(0.5)
            #print("Function %s is a guard and its value is %s" % (self.fun.id, decision))

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
            
            #print("taken: %s" % taken_branch)
            
            # delete discarded function and all functions which was depending
            deleted_functions = delete_functions_chain_by_id(self.application.chain, discarded_branch)
            # release resources
            for fun in deleted_functions:
                self.application.placement[fun].state = FunctionState.CANCELED
                node_id = self.application.placement[fun].node_id
                node : Node = self.application.infrastructure_nodes[node_id]
                node.release_resources(self.application.placement[fun].memory, self.application.placement[fun].v_cpu)

            # execute the taken function
            fun_process = FunctionProcess(self.application.placement[taken_branch], self.env, self.application)
            self.application.function_processes.append(fun_process)
        
        else:
            # execute the functions
            for fun in to_execute:
                fun_process = FunctionProcess(self.application.placement[fun], self.env, self.application)
                self.application.function_processes.append(fun_process)
        
        # free node memory
        fun_name = self.fun.id
        node_id = self.application.placement[fun_name].node_id
        node : Node = self.application.infrastructure_nodes[node_id]
        node.release_resources(self.application.placement[fun_name].memory, self.application.placement[fun_name].v_cpu)
