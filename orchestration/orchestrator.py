import threading
import simpy
from application.application import Application, ApplicationState

from orchestration.function_process import FunctionProcess
from utils import get_ready_functions


class Orchestrator(threading.Thread):
    def __init__(self, env: simpy.Environment, application: Application):
        super().__init__()
        self.env = env
        self.application = application

    def run(self):

        # get first functions to execute from the chain
        ready_functions: list = get_ready_functions(self.application.chain)

        # set application as running
        self.application.state = ApplicationState.RUNNING

        # execute ready functions
        for function_name in ready_functions:
            fun_process = FunctionProcess(
                self.application.placement[function_name], self.env, self.application
            )
            self.application.function_processes[function_name] = fun_process
