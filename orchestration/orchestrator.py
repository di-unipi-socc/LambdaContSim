import threading
import simpy
from application.application import Application, ApplicationState

from orchestration.function_process import FunctionProcess
from utils import get_ready_functions

class Orchestrator(threading.Thread):

    def __init__(self, thread_name, thread_ID, env : simpy.Environment, application : Application):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.env = env
        self.application = application
    
    def run(self):
        
        # get first functions to execute from the chain
        ready_functions : list = get_ready_functions(self.application.chain)

        # set application as running
        self.application.state = ApplicationState.RUNNING

        # execute ready functions
        for fun in ready_functions:
            fun_process = FunctionProcess(self.application.placement[fun], self.env, self.application)
            self.application.function_processes.append(fun_process)

