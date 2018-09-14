from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


class PostInstallCommand(install):
    def run(self):
        import os, shutil
        from jobserver.app import APP_PATH

        # rename the config file
        if not os.path.exists(os.path.join(APP_PATH, 'config.py')):
            shutil.copy(
                os.path.join(APP_PATH, 'config.py.default'),
                os.path.join(APP_PATH, 'config.py')
            )

        install.run()

class PostDevelopCommand(develop):
    def run(self):
        import os, shutil
        from jobserver.app import APP_PATH

        # rename the config file
        if not os.path.exists(os.path.join(APP_PATH, 'config.py')):
            shutil.copy(
                os.path.join(APP_PATH, 'config.py.default'),
                os.path.join(APP_PATH, 'config.py')
            )

        develop.run()

def readme():
    with open('README.rst') as f:
        return f.read().strip()


def version():
    with open('VERSION') as f:
        return f.read().strip()


def requirements():
    with open('requirements.txt') as f:
        return f.read().strip().split('\n')


def classifiers():
    with open('classifiers.txt') as f:
        return f.read().strip().split('\n')


setup(name='jobserver',
      license='GNU GPL 3',
      version=version(),
      author='Mirko Maelicke',
      author_email='mirko.maelicke@kit.edu',
      description='RESTful Flask application for running Python code',
      long_description=readme(),
      classifiers=classifiers(),
      install_requires=requirements(),
      packages=find_packages(),
      cmdclass = {
          'develop': PostDevelopCommand,
          'install': PostInstallCommand
      },
      include_package_data=True,
      zip_safe=False
)
