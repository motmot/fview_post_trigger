from setuptools import setup, find_packages
import sys,os

setup(name='motmot.fview_post_trigger',
    description='post trigger movie saving plugin for FView',
    version='0.0.1',
    packages = find_packages(),
    author='Andrew Straw',
    author_email='strawman@astraw.com',
    url='http://code.astraw.com/projects/motmot',
    entry_points = {
  'motmot.fview.plugins':
  'fview_post_trigger = motmot.fview_post_trigger.fview_post_trigger:FviewPostTrigger',
  },
    )
