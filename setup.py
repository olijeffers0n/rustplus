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
      version="2.1",
      include_package_data=True,
      packages = ['rustplus', 'rustplus.api', 'rustplus.api.icons', 'rustplus.exceptions', 'rustplus.objects', 'rustplus.utils'],
      license='MIT',
      description='A python wrapper for the Rust Plus API',
      long_description=readme,
      long_description_content_type='text/markdown',
      install_requires=[
        "Pillow",
        "websocket-client",
        "protobuf"
      ],
      python_requires='>=3.7.0',
)