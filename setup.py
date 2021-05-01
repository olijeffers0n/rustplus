from distutils.core import setup
setup(
  name = 'rustplus',         
  packages = ['rustplus'],   
  version = '1.0',      
  license='MIT',        
  description = 'An API Wrapper for the Rust+ API',   
  author = 'olijeffers0n',                   
  author_email = 'pleaseUseMyDiscord@Please.com',      
  url = 'https://github.com/olijeffers0n/rustplus',   
  download_url = 'https://github.com/olijeffers0n/rustplus/archive/refs/tags/1.0.tar.gz',    # I explain this later on
  keywords = ['Rust+', 'APIWrapper', 'Time', 'Map'],   
  install_requires=[            
          'Pillow',
          'websocket-client',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
  ],
)