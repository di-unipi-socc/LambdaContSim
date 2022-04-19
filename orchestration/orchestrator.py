import threading
import simpy
from application.function import PlacedFunction

from orchestration.function_process import FunctionProcess
from utils import delete_executed_function, get_ready_functions
from infrastructure.node import Node

class Orchestrator(threading.Thread):

    def __init__(self, thread_name, thread_ID, infrastructure, functions_chain, placement):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.infrastructure : dict[str, Node] = infrastructure
        self.function_chain = functions_chain
        self.placement = placement
    
    def run(self):
        env = simpy.Environment()
        
        # find the next function(s) to execute from the chain
        functions_name : list = get_ready_functions(self.function_chain)
        #print(functions_name)
        for fun in functions_name:
            delete_executed_function(self.function_chain, fun)

        start_functions = []
        for fun in functions_name:
            fun_process = FunctionProcess(self.placement[fun], env, self.infrastructure, self.function_chain, self.placement)
        
        env.run(until=30)

        print("finished")
