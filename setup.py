from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-notification_api',
    version=version,
    description="",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='JanosFarkas',
    author_email='farkas48@uniba.sk',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.notification_api'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        notification_api=ckanext.notification_api.plugin:NotificationApiPlugin
        [ckan.celery_task]
        tasks = ckanext.notification_api.celery_import:task_imports
    ''',
)
