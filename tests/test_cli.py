import os
import re
import subprocess
from typing import Callable
import unittest
import time
import datetime
from datetime import timedelta
from uuid import uuid4

BEANSTALKD_PATH = os.getenv("BEANSTALKD_PATH", "beanstalkd")
DEFAULT_INET_ADDRESS = ("127.0.0.1", 4444)

TestFunc = Callable[[], None]
WrapperFunc = Callable[[], None]
DecoratorFunc = Callable[[TestFunc], WrapperFunc]

def with_beanstalkd() -> DecoratorFunc:

    def decorator(test: TestFunc) -> WrapperFunc:

        def wrapper(cls) -> None:
            cmd = [BEANSTALKD_PATH]
            host = '127.0.0.1'
            port = 11300
            address = (host,port)
            cmd.extend(["-l", host, "-p", str(port)])
            print(f'starting beanstalkd [{cmd=}][{address=}]')
            with subprocess.Popen(cmd) as beanstalkd:
                print(f'started beanstalkd {beanstalkd.pid=}')
                time.sleep(0.1)
                try:
                    test(cls)
                finally:
                    print(f'terminating beanstalkd {beanstalkd.pid=}')
                    beanstalkd.terminate()

        return wrapper

    return decorator

class TestCli(unittest.TestCase):
    def get_tubename(self) :
        return  f'unit-test-queue-{uuid4()}'

    def run_cli(self, command, tubename , additional_args=[]):
        args = []
        args.append('python3')
        args.append('pulpo-beanstalk-cli/pulpo-beanstalk-cli.py')
        args.append(command)
        args.append('-s=127.0.0.1')
        args.append('-p=11300')
        print('using tube:', tubename)
        args.append(f'--tube={tubename}')
        args = args + additional_args
        for arg in additional_args:
            args.append(arg)
        result= subprocess.run(args, capture_output=True)
        print(f'{command=} => {result=}')
        return result
        
    def get_job_id_from_output(self, result):
        output = result.stdout
        # Decode bytes to string
        output_str = output.decode('utf-8')
        match = re.search(r'job_id=(\d+)', output_str)

        self.assertIsNotNone(match, f'unable to determine job id from output [{output_str}]')
        job_id = match.group(1)
        return job_id
        
    def test_ls(self):
        result = subprocess.run(["ls", "-l", "/dev/null"], capture_output=True)            
        print(result)
        assert result.returncode == 0
        assert 'root' in str(result.stdout)

    @with_beanstalkd()
    def test_put(self):
        tubename = self.get_tubename()
        additional_args = ['--body=sample']
        result =self.run_cli(command='put', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0

        job_id = self.get_job_id_from_output(result)
        print(f'{job_id=}')
        self.assertIsNotNone(job_id)

    @with_beanstalkd()
    def test_put_peek(self):
        tubename = self.get_tubename()
        additional_args = ['--body=sample']
        result =self.run_cli(command='put', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0

        job_id = self.get_job_id_from_output(result)
        print(f'{job_id=}')
        self.assertIsNotNone(job_id)

        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='peek', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0
        assert 'sample' in str(result.stdout)

    @with_beanstalkd()
    def test_put_pop_peek(self):
        tubename = self.get_tubename()
        additional_args = ['--body=sample']
        result =self.run_cli(command='put', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0

        job_id = self.get_job_id_from_output(result)
        print(f'{job_id=}')
        self.assertIsNotNone(job_id)

        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='peek', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0
        assert 'sample' in str(result.stdout)

        print(f'pop {job_id=}')
        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='pop', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0

        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='peek', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 1

    @with_beanstalkd()
    def test_put_delete_peek(self):
        tubename = self.get_tubename()
        additional_args = ['--body=sample']
        result =self.run_cli(command='put', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0

        job_id = self.get_job_id_from_output(result)
        print(f'{job_id=}')
        self.assertIsNotNone(job_id)

        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='peek', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0
        assert 'sample' in str(result.stdout)

        print(f'pop {job_id=}')
        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='delete', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 0

        additional_args = [f'--id={job_id}']
        result =self.run_cli(command='peek', tubename=tubename , additional_args=additional_args  )
        assert result.returncode == 1

    @with_beanstalkd()
    def test_pop_empty(self):
        tubename = self.get_tubename()
        result =self.run_cli(command='pop', tubename=tubename )
        assert result.returncode == 0
        assert 'no message available' in str( result.stdout)

    @with_beanstalkd()
    def test_peek_no_job_id(self):
        tubename = self.get_tubename()
        result =self.run_cli(command='peek', tubename=tubename )
        assert result.returncode == 1
        assert 'invalid job id' in str( result.stderr)

    @with_beanstalkd()
    def test_delete_no_job_id(self):
        tubename = self.get_tubename()
        result =self.run_cli(command='peek', tubename=tubename )
        assert result.returncode == 1
        assert 'invalid job id' in str( result.stderr)

    @with_beanstalkd()
    def test_invalid_command(self):
        tubename = self.get_tubename()
        result =self.run_cli(command='invalidcode', tubename=tubename , additional_args=[]  )
        assert result.returncode != 0

