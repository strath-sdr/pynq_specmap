import os
import shutil
from distutils.dir_util import copy_tree

from setuptools import find_packages, setup

# global variables
repo_notebook_folder = f'notebooks'
repo_asset_folder = f'assets'
board_notebooks_dir = os.environ['PYNQ_JUPYTER_NOTEBOOKS']
package_name = 'pynq_specmap'
data_files = []

# copy notebooks to jupyter home
def copy_notebooks():
    src_dir = os.path.join(repo_notebook_folder)
    dst_dir = os.path.join(board_notebooks_dir, 'spectrum-map')
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    copy_tree(src_dir, dst_dir)
    data_files.extend(
        [os.path.join("..", dst_dir, f) for f in os.listdir(dst_dir)])
    
# copy assets to package folder
def copy_assets():
    src_dir = os.path.join(repo_asset_folder)
    dst_dir = os.path.join(package_name, 'assets')
    copy_tree(src_dir, dst_dir)
    data_files.extend(
        [os.path.join("..", dst_dir, f) for f in os.listdir(dst_dir)])

copy_notebooks()
copy_assets()

setup(
    name=package_name,
    version='0.2.0',
    install_requires=[
        'pynq==2.7.0',
        'plotly==5.1.0',
        'pandas==1.3.3',
        'requests==2.22.0',
        'json5==0.9.5',
        'pickleshare==0.7.5',
    ],
    author="David Northcote",
    packages=find_packages(),
    package_data={
        '': data_files,
    },
    description="PYNQ Spectrum Mapping Tools.")
