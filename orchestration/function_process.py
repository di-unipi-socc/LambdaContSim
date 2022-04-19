# this class represent a simpy process which runs a particular function

import simpy

from application.function import PlacedFunction
from infrastructure.node import Node
from utils import delete_executed_function, get_ready_functions

class FunctionProcess:
    def __init__(self, fun : PlacedFunction, env : simpy.Environment, infrastructure, chain, placement):
        self.fun = fun

        self.env = env

        self.action = env.process(self.run())

        self.infrastructure = infrastructure
        self.chain = chain

        self.placement = placement

    def run(self):
        duration = 5
        yield self.env.timeout(duration)

        print("%s finished" % self.fun.id)

        functions_name : list = get_ready_functions(self.chain)
        # delete from chain
        # TODO RIVEDI
        for fun in functions_name:
            delete_executed_function(self.chain, fun)

        for fun in functions_name:
            fun_process = FunctionProcess(self.placement[fun], self.env, self.infrastructure, self.chain, self.placement)
        
        # free node memory
        fun_name = self.fun.id
        node_id = self.placement[fun_name].node_id
        node : Node = self.infrastructure[node_id]
        node.give_back_resources(self.placement[fun_name].memory, self.placement[fun_name].v_cpu)
