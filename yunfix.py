#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: BaiduYunSyncFix
# Filename: fix
# Created on: 2023/8/10

from os import remove, walk, system
from pathlib import Path
from i2cylib.utils.args import get_args
from i2cylib.utils.logger import Logger
from multiprocessing import Process, Queue, Manager, freeze_support
from tqdm import tqdm
from time import time


def manual():
    print("""
    =========================================================
        BaiduYun Sync Space .git repository file fixer
    ====================[v 0.1 by I2cy]======================
    
    this fixer will try to fix the 'unable to sync' problem
    from BaiduYun Sync Space in target directory including
    its sub directories using multiprocessing. 
    
    Usage: yunfix [-m num_of_subprocess] [-t directory] [-h]
    
    Args:
      -t --target       - target root path for processing, [default current directory]
      -h --help         - display this manual
    
    Examples:
    > yunfix
    > yunfix -t MySyncSpace
    """)


class Fixer:

    def __init__(self, target_path: Path, num_of_threads: int, logger: Logger = None):
        self.root = target_path
        self.logger = logger

        # flags
        self.debug = False

        # initialize multi-processing manager
        self.mul_manager = Manager().dict({"live": True,
                                           "fixed_directories": 0,
                                           "fixed_files": 0,
                                           "debug": self.debug})

        self.queues = Queue(-1)

        self.workers = [Worker(wid, self) for wid in range(num_of_threads)]

    def kill(self):
        self.mul_manager['live'] = False
        for ele in self.workers:
            ele.wait_for_kill()

    def start(self):
        dirs = 0
        t0 = time()  # record start time
        # start sub progresses
        self.workers[0].run()

        self.logger.INFO("scanning target path \"{}\" and its sub directories for corruption".format(
            self.root.as_posix()))

        td = tqdm(total=100, unit='%')
        td.set_description_str("{} dir(s) found, {} file(s) fixed, Progress".format(0, 0), refresh=True)

        try:
            t1 = time()
            # walk through target directories and its subdirectories
            for root, path, file in walk(self.root):
                for name in path:
                    # distribute task for workers
                    self.queues.put(Path(root).joinpath(name), block=True)
                    dirs += 1

                    t2 = time()
                    if t2 - t1 > 0.5:
                        t1 = time()
                        # update progress bar
                        td.set_description_str(
                            "{} dir(s) found, {} file(s) fixed, Progress".format(
                                dirs, self.mul_manager['fixed_files']),
                            refresh=True
                        )

            td.set_description_str(
                "{} dir(s) found, {} file(s) fixed, Progress".format(
                    dirs, self.mul_manager['fixed_files']),
                refresh=True
            )

            # update progress bar after all path scanned
            while self.mul_manager['fixed_directories'] < dirs:
                t2 = time()
                if t2 - t1 > 0.5:
                    t1 = time()
                    # if sum([ele.queue.qsize() for ele in self.workers]) == 0:
                    #     break
                    if dirs > 0:
                        td.n = 100 * self.mul_manager['fixed_directories'] // dirs
                        td.refresh()

            td.n = 100

            # stop progress bar
            td.close()

        except Exception as err:
            td.close()
            self.logger.ERROR("error while processing, {}".format(err))

        self.logger.INFO("operation complete, {} file(s) fixed and {} dir(s) scanned, total time spent {:.1f} s".format(
            self.mul_manager['fixed_files'],
            self.mul_manager['fixed_directories'],
            time() - t0
        ))

        self.logger.DEBUG("waiting for all subprocesses to kill")
        self.kill()


class Worker:

    def __init__(self, wid: int, parent: Fixer):
        self.id = wid
        self.mul_manager = parent.mul_manager
        self.queue = parent.queues

        self.sub_process = Process(target=self.mul_proc)
        self.started = False

    def mul_proc(self):
        total_fix = 0
        while self.mul_manager['live']:
            try:
                path: Path = self.queue.get(block=True, timeout=0.02)
            except Exception:
                continue

            if path is None:
                continue
            corrupted = [ele for ele in path.glob('*(*).baiduyun.downloading') if ele.is_file()]

            if len(corrupted):
                # if corruption found

                fixed = 0
                for ele in corrupted:
                    old_file = path.joinpath(ele.name[:-24])
                    if ele.is_file() and old_file.exists():
                        if old_file.stat().st_mtime_ns < ele.stat().st_mtime_ns:
                            # remove older file
                            try:
                                system(f"attrib -r \"{old_file.as_posix()}\"")
                                remove(old_file.as_posix())
                                fixed += 1
                            except Exception as err:
                                pass
                        else:
                            # uncheck file "READ-ONLY" status
                            try:
                                system(f"attrib -r \"{old_file.as_posix()}\"")
                                fixed += 1
                            except Exception as err:
                                pass

                self.mul_manager['fixed_files'] += fixed

            self.mul_manager['fixed_directories'] += 1
            total_fix += 1

    def run(self):
        self.started = True
        self.sub_process.start()

    def wait_for_kill(self):
        if self.started:
            self.sub_process.join()


def main():
    # initialize logger
    logger = Logger(date_format="%H:%M:%S")
    fixer = None

    try:
        # get args
        opts = get_args()

        # initialize defaults
        mp_num = 1
        target_path = "./"

        # phrasing keywords
        for key in opts:
            if key in ('-h', '--help'):
                # print manual
                manual()
                return

            elif key in ('-t', '--target'):
                # set target path
                target_path = opts[key]

            else:
                pass

        # path check
        try:
            root_path = Path(target_path)
            if not root_path.exists():
                # if path does not exist, raise exception
                raise Exception(f"\"{target_path}\" not found")
        except Exception as err:
            logger.ERROR(str(err))
            return

        # start, scan and fix
        fixer = Fixer(root_path, mp_num, logger)
        fixer.start()
    except KeyboardInterrupt:
        logger.INFO("operation interrupted by user")
        if fixer is not None:
            fixer.kill()


if __name__ == "__main__":
    freeze_support()
    main()
