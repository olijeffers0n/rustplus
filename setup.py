from setuptools import setup, find_packages


def main() -> None:
    version = ""
    with open("src/rustplus/__init__.py") as input_file:
        for line in input_file.readlines():
            if line.startswith("__version__"):
                version = line.strip("__version__ =").strip().strip('"')
                break

    with open("README.md", errors='ignore') as input_file:
        readme = input_file.read()

    setup(
        name='rustplus',
        author='olijeffers0n',
        url='https://github.com/olijeffers0n/rustplus',
        project_urls={
            "Issue tracker": "https://github.com/olijeffers0n/rustplus/issues",
        },
        package_dir={"": "src"},
        version=version,
        packages=find_packages(where='src'),
        license='MIT',
        description='A python wrapper for the Rust Plus API',
        long_description=readme,
        long_description_content_type='text/markdown',
        install_requires=[
            "websocket_client",
            "Pillow",
            "protobuf==4.21.1",
            "asyncio",
            "rustPlusPushReceiver==0.4.0",
            "http-ece",
            "requests"
        ],
        python_requires='>=3.7.0',
    )


if __name__ == "__main__":
    main()
