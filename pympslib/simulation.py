from .entity.SNESIMTree import SNESIMTree
from .ENESIM import start_simulation
from .DS import cSimulation
from .utils.Etype import DrawEtype


def snesim(parameter_file):
    aSimulation = SNESIMTree(parameter_file)
    aSimulation.startSimulation()

def enesim(parameter_file):
    start_simulation(parameter_file)

def ds(parameter_file):
    cSimulation(parameter_file)


