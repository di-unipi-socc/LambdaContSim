import threading
import simpy

from orchestration.function_process import FunctionProcess
from utils import delete_executed_function, get_ready_functions
from infrastructure.node import Node

class Orchestrator(threading.Thread):

    def __init__(self, thread_name, thread_ID, env : simpy.Environment, infrastructure, application_chain, placement):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.env = env
        self.infrastructure : dict[str, Node] = infrastructure
        self.application_chain = application_chain
        self.placement = placement
    
    def run(self):
        
        # get first functions to execute from the chain
        ready_functions : list = get_ready_functions(self.application_chain)

        # execute ready functions
        for fun in ready_functions:
            fun_process = FunctionProcess(self.placement[fun], self.env, self.infrastructure, self.application_chain, self.placement)

