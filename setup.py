from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in gbs_attendance/__init__.py
from gbs_attendance import __version__ as version

setup(
	name="gbs_attendance",
	version=version,
	description="Gbs Attendance",
	author="kazemaraby@gmail.com",
	author_email="kzemaraby@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
