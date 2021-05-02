from setuptools import setup

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
      name='rustplus',
      author='olijeffers0n',
      author_email='pleaseUseMyDiscord@Please.com',
      url='https://github.com/olijeffers0n/rustplus',
      project_urls={
        "Issue tracker": "https://github.com/olijeffers0n/rustplus/issues",
      },
      version="1.1.1",
      include_package_data=True,
      packages = ['rustplus', 'rustplus.api', 'rustplus.api.icons', 'rustplus.exceptions'],
      license='MIT',
      description='A python wrapper for the Rust Plus API',
      long_description=readme,
      long_description_content_type='text/markdown',
      install_requires=[
        "Pillow",
        "websocket-client"
      ],
      python_requires='>=3.7.0',
)
