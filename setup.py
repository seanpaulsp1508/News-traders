from setuptools import setup, find_packages

setup(
    name="news-trading-platform",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "web3>=5.0.0",
        "pandas>=1.3.0",
        "transformers>=4.15.0",
        # ... other dependencies from requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "news-trader=scripts.execute_trades:main",
            "deploy-contracts=scripts.deploy_contracts:main",
        ],
    },
)
