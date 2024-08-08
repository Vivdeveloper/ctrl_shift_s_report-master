from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ctrl_shift_s_report/__init__.py
from ctrl_shift_s_report import __version__ as version

setup(
	name="ctrl_shift_s_report",
	version=version,
	description="(Ctrl + Shift + S)",
	author="Software At Work (India) Pvt. Ltd.",
	author_email="erp@sawindia.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
