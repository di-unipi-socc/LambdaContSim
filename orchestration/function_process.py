# this class represent a simpy process which runs a particular function

import simpy

from application.placed_function import FunctionState, PlacedFunction
from infrastructure.node import Node
from utils import delete_executed_function, delete_functions_chain_by_id, get_next_functions_by_id, get_ready_functions, take_decision

class FunctionProcess:
    def __init__(self, fun : PlacedFunction, env : simpy.Environment, infrastructure, application_chain, placement):
        self.fun = fun

        self.env = env

        self.action = env.process(self.run())

        self.infrastructure = infrastructure
        self.application_chain = application_chain

        self.placement = placement

    def run(self):

        # function is running
        self.fun.state = FunctionState.RUNNING

        duration = 1
        yield self.env.timeout(duration)

        # function exited
        self.fun.state = FunctionState.EXITED

        #print("Function %s finished" % self.fun.id)

        # get functions which depends on me
        dependent_functions : list = get_next_functions_by_id(self.application_chain, self.fun.id)
        
        # delete myself from the chain
        delete_executed_function(self.application_chain, self.fun.id)

        # get ready functions
        ready_functions : list = get_ready_functions(self.application_chain)

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
            print("Function %s is a guard and its value is %s" % (self.fun.id, decision))

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
            deleted_functions = delete_functions_chain_by_id(self.application_chain, discarded_branch)
            # release resources
            for fun in deleted_functions:
                self.placement[fun].state = FunctionState.CANCELED
                node_id = self.placement[fun].node_id
                node : Node = self.infrastructure[node_id]
                node.release_resources(self.placement[fun].memory, self.placement[fun].v_cpu)

            # execute the taken function
            fun_process = FunctionProcess(self.placement[taken_branch], self.env, self.infrastructure, self.application_chain, self.placement)
        
        else:
            # execute the functions
            for fun in to_execute:
                fun_process = FunctionProcess(self.placement[fun], self.env, self.infrastructure, self.application_chain, self.placement)
        
        # free node memory
        fun_name = self.fun.id
        node_id = self.placement[fun_name].node_id
        node : Node = self.infrastructure[node_id]
        node.release_resources(self.placement[fun_name].memory, self.placement[fun_name].v_cpu)
