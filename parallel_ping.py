#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import subprocess


class ParallelPing(object):
    """ do parallel ping """
    def __init__(self, **kwargs):
        self.targets = kwargs['targets']
        self.retry_count = kwargs['count']
        self.max_workers = kwargs['max_workers']
        self.sysname = self.get_sysname()
        self.ping_args = self.generate_ping_args(kwargs)
        self.results = None

    def get_sysname(self):
        sysname = os.uname().sysname
        supported_os = ['Darwin', 'Linux']

        if sysname in supported_os:
            return sysname
        else:
            raise NotImplementedError('Unsupported OS')

    def generate_ping_args(self, kwargs):
        """
        generate ping options. supporting count and timeout.
       
        rtype: list
        """
        try:
            timeout = str(kwargs['timeout'])
        except KeyError:
            raise

        if self.sysname == 'Darwin':
            return ['-n', '-q', '-t', timeout, '-c', '1']
        elif self.sysname == 'Linux':
            return ['-n', '-q', '-W', timeout, '-c', '1']

    def get_ping_result(self, target):
        """
        ping to single target
        """
        command = ['ping', target]
        command.extend(self.ping_args)

        count = 0
        while count < self.retry_count:
            res = subprocess.run(command, capture_output=True)
            if res.returncode == 0:
                return res
            else:
                count += 1
        return res

    def run(self):
        """
        parallel ping using concurrent.futures.TheadPoolExecutor
        """
        self.results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            res = [e.submit(self.get_ping_result, target)
                for target in self.targets]
            for future in as_completed(res):
                self.results.append(future.result())

    def get_active_target_count(self):
        return len([ r for r in self.results if r.returncode == 0 ])

    def print_stdout(self):
        for r in self.results:
            print(r.stdout.decode('utf-8'))
            

@click.command()
@click.option('--target', '-t', multiple=True, type=str)
@click.option('--timeout', '-T', default=1)
@click.option('--count', '-c', default=3)
@click.option('--max-workers', default=10)
@click.option('--output', type=click.Choice(['active-count', 'stdout']))
def cmd(target, timeout, count, max_workers, output):
    pping = ParallelPing(
        targets=list(target), timeout=timeout,
        count=count, max_workers=max_workers)
    pping.run()

    if output == 'active-count':
        print(pping.get_active_target_count())
    elif output == 'stdout':
        pping.print_stdout()
    else:
        pass


if __name__ == '__main__':
    cmd()
