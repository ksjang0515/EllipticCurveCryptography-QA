from dwave.system import DWaveSampler, EmbeddingComposite
from dimod.binary import BinaryQuadraticModel
from dimod.vartypes import Vartype
from dimod import ExactSolver
from dimod.sampleset import SampleSet


class BaseController:
    def __init__(self) -> None:
        self.bqm = BinaryQuadraticModel(Vartype.BINARY)

        self.dwave_sampler = None
        self.embedding_sampler = None

    def get_sampler(self):
        self.dwave_sampler = DWaveSampler()
        print("QPU {} was selected.".format(self.dwave_sampler.solver.name))

        self.embedding_sampler = EmbeddingComposite(self.dwave_sampler)

    def run_DWaveSampler(self, num_reads: int = 100, label: str = 'controller') -> SampleSet:
        if not self.embedding_sampler:
            self.get_sampler()

        solution = self.embedding_sampler.sample(
            self.bqm, num_reads=num_reads, label=label)

        return solution

    def run_ExactSolver(self) -> SampleSet:
        solver = ExactSolver()
        solution = solver.sample(self.bqm)

        return solution

    @property
    def shape(self) -> int:
        return self.bqm.shape

    def _add_variable(self, bit, bias: int = 0) -> None:
        self.bqm.add_variable(bit, bias)

    def _add_quadratic(self, bit1, bit2, bias: int) -> None:
        self.bqm.add_quadratic(bit1, bit2, bias)

    def _flip_variable(self, bit) -> None:
        self.bqm.flip_variable(bit)

    def _add_offset(self, v: int):
        self.bqm.offset += v
