<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

# 百度云同步空间修复器
#### BaiduYun SyncSpace Fixer


_+ [BaiduYunSyncFix Github Page 链接](https://github.com/i2cy/BaiduYunSyncFix) +_

</div>

<p align="center">
  <a href="https://github.com/i2cy/BaiduYunSyncFix/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/i2cy/BaiduYunSyncFix.svg" alt="license">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## 摘要 Abstract
本工具旨在解决百度云同步空间在同步git仓库项目时出现的‘文件移动失败’导致同步错误的问题，
其本质是部分文件被误设为只读模式，导致程序无法覆盖移动。

本工具是命令行工具，需要在终端中执行，其使用方法请见下文。

## 特点 Features
  1. 自动遍历目标及其子目录寻找引起同步失效的文件
  2. 使用多进程分离扫描、处理环节，处理速度快
  3. 具有进度条提示

## 样例 Examples
  1. 不加参数直接运行，扫描当前目录及子目录

         PS E:\BaiduSyncdisk> yunfix

         [23:45:42] [INFO] scanning target path "." and its sub directories for corruption
         9571 dir(s) found, 0 file(s) fixed, Progress: 100%|███████████████████████████████████| 100/100 [00:06<00:00, 14.35%/s]
         [23:45:49] [INFO] operation complete, 0 file(s) fixed and 9571 dir(s) scanned, total time spent 7.0 s
         [23:45:49] [DBUG] waiting for all subprocesses to kill

  2. 指定目录扫描，使用参数`-t <target_directory_目标目录>`

         PS E:\BaiduSyncdisk> yunfix -t .\PycharmProjects\

         [11:03:21] [INFO] scanning target path "PycharmProjects" and its sub directories for corruption
         1904 dir(s) found, 0 file(s) fixed, Progress: 100%|██████████████████████████████████████████| 100/100 [00:01<00:00, 76.54%/s]
         [11:03:23] [INFO] operation complete, 0 file(s) fixed and 1904 dir(s) scanned, total time spent 1.3 s
         [11:03:23] [DBUG] waiting for all subprocesses to kill

  3. 查看帮助，使用参数`-h`

         PS E:\BaiduSyncdisk> yunfix -h

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

## 安装 Installation
下载Release中的可执行文件即可

## 依赖 Requirements
`Python >= 3.7`
`i2cylib >= 1.12.6`
`tqdm`

## Update Notes

#### 2023-08-11
 1. 进行了简单有效测试的初代版本v0.1发布