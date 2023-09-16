"""
MIT License

Copyright (c) 2020 André Lousa Marques <andre.lousa.marques at gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
from pathlib import Path
import subprocess
import zipfile
import tarfile
from os import mkdir, chmod, environ
from shutil import rmtree
import sys

DEPS_DIR = "worky_deps"

# PEP600: manylinux_${GLIBCMAJOR}_${GLIBCMINOR}_${ARCH}
# Currently using PEP 599 below. To be replaced at some point by PEP600 above
LINUX64_PLATFORM = "manylinux2014_x86_64"
WIN_PLATFORM = "win_amd64"

if sys.platform.startswith("linux"):
    PIPENV_BIN_DIR = "bin"
elif sys.platform.startswith("win32"):
    PIPENV_BIN_DIR = "Script"
else:
    raise Exception("Unsupported platform")

SELENIUM_DRIVER_PATH = Path(".env") / PIPENV_BIN_DIR


def get_deps_tar_file(platform):
    return "%s_%s.tar.gz" % (DEPS_DIR, platform)


def install_selenium():
    selenium_driver_zip = Path("selenium") / "chromedriver.zip"

    if not SELENIUM_DRIVER_PATH.joinpath("chromedriver").exists():
        if not selenium_driver_zip.exists():
            raise Exception("Please provide a suitable selenium driver for "
                            "your chrome browser and place it at %s"
                            % selenium_driver_zip)

        with zipfile.ZipFile(str(selenium_driver_zip), 'r') as driver:
            driver.extractall(str(SELENIUM_DRIVER_PATH))

        chmod(str(SELENIUM_DRIVER_PATH / "chromedriver"), 744)


def install():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                           'requirements.txt'])


def offline_install(platform):
    with tarfile.open(get_deps_tar_file(platform), "r:gz") as deps_tar:
        deps_tar.extractall()

    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                           'requirements.txt', '--no-index', '--find-links',
                           DEPS_DIR])


def package(platform):
    mkdir(DEPS_DIR)

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'download', '-r',
                               'requirements.txt', '--platform', platform,
                               '--python-version', '311',
                               '--only-binary=:all:', '-d', DEPS_DIR])

        with tarfile.open(get_deps_tar_file(platform), "x:gz") as deps_tar:
            deps_tar.add(DEPS_DIR)
    finally:
        rmtree(DEPS_DIR)


def _run_tests():
    subprocess.check_call(['pytest', '--cov=worky', '--cov-report=term',
                           '--cov-report=xml:coverage_report.xml',
                           '-o', 'junit_family=xunit2',
                           '--junitxml=test_reports.xml', 'tests'])


def run_tests_local():
    install_selenium()

    _run_tests()


def run_tests_remote():
    environ["REMOTE_SELENIUM"] = "localhost"

    _run_tests()


def run_tests_ci():
    environ["REMOTE_SELENIUM"] = "selenium__standalone-chrome"

    _run_tests()


def run_flake8():
    subprocess.check_call(['flake8', '--exclude', '.env'])


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    options = arg_parser.add_mutually_exclusive_group()

    options.add_argument("--install", help="Install worky using the internet",
                         action="store_true")
    options.add_argument("--offline-install-linux64", help="Install worky "
                         "using the pre-packed dependencies at "
                         "worky_deps_%s.tar.gz" % LINUX64_PLATFORM,
                         action="store_true")
    options.add_argument("--offline-install-win64", help="Install worky using "
                         "the pre-packed dependencies at worky_deps_%s.tar.gz"
                         % WIN_PLATFORM, action="store_true")
    options.add_argument("--run-tests-local", help="Run the testsuite and "
                         "show coverage metrics. Requires chrome to be "
                         "installed", action="store_true")
    options.add_argument("--run-tests-remote", help="Run the testsuite and "
                         "show coverage metrics. Requires selenium server "
                         "and chrome to be installed", action="store_true")
    options.add_argument("--run-tests-ci", help="Run the testsuite and "
                         "show coverage metrics. To be used by gitlab CI",
                         action="store_true")
    options.add_argument("--package-linux64", help="Download and package the "
                         "project dependencies for linux 64bit",
                         action="store_true")
    options.add_argument("--package-win64", help="Download and package the "
                         "project dependencies for windows 64bit",
                         action="store_true")
    options.add_argument("--lint", help="Run flake8 against the project",
                         action="store_true")

    args = arg_parser.parse_args()

    try:
        if args.install:
            install()
        elif args.offline_install_linux64:
            offline_install(LINUX64_PLATFORM)
        elif args.offline_install_win64:
            offline_install(WIN_PLATFORM)
        elif args.run_tests_local:
            run_tests_local()
        elif args.run_tests_remote:
            run_tests_remote()
        elif args.run_tests_ci:
            run_tests_ci()
        elif args.package_linux64:
            package(LINUX64_PLATFORM)
        elif args.package_win64:
            package(WIN_PLATFORM)
        elif args.lint:
            run_flake8()
        else:
            arg_parser.print_help()
    except subprocess.CalledProcessError as e:
        exit(e.returncode)
    except Exception as e:
        print(e)
