from unittest.mock import Mock
from pytest_mock import MockFixture
from civet.bases import DataFile, DataSource
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExampleDataFile(DataFile['ExampleDataFile']):

    do_something_command: Mock = field(default_factory=Mock)
    do_another_command: Mock = field(default_factory=Mock)

    def __post_init__(self):
        self.do_something_command.return_value = ['one', 'two', 'three']
        self.do_another_command.return_value = ['four', 'five']

    def do_something(self) -> 'ExampleDataFile':
        return self.create_command(self.do_something_command)

    def do_another(self) -> 'ExampleDataFile':
        return self.create_command(self.do_another_command)


@dataclass(frozen=True)
class ExampleComposite(DataSource):
    in1: ExampleDataFile
    in2: ExampleDataFile

    def command(self, output):
        # calling self.in1.do_something() twice should only execute the underlying command once
        something1 = self.in1.do_something()
        # the second call to self.in1.do_something() here should hit the cache
        whatever = self.in1.do_something().do_another()
        another2 = self.in2.do_another()
        return 'foo', something1, whatever, another2, output


def test_uses_cache(mocker: MockFixture):
    shell = mocker.Mock()
    thing1 = ExampleDataFile('dne1')
    thing2 = ExampleDataFile('dne2')
    composite = ExampleComposite(thing1, thing2)

    composite.save('result_path', require_output=False, shell=shell)

    thing1.do_something_command.assert_called_once()
    thing2.do_another_command.assert_called_once()

    something1_cache, = thing1.do_something_command.call_args.args
    another2_cache, = thing2.do_another_command.call_args.args

    shell.assert_any_call(('foo', something1_cache, mocker.ANY, another2_cache, mocker.ANY))
