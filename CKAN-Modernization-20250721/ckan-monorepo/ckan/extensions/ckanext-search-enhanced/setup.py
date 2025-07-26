from setuptools import setup, find_packages

version = "0.1.0"

setup(
    name="ckanext-search-enhanced",
    version=version,
    description="Advanced Search & Discovery enhancements for CKAN Phase 3",
    long_description="""
    Enhanced search functionality for CKAN including:
    - City-specific faceted search (department, update frequency, geographic coverage)
    - Related datasets recommendations
    - Search analytics integration
    - Improved search UI components
    """,
    classifiers=[],
    keywords="",
    author="CKAN Team",
    author_email="info@ckan.org",
    url="",
    license="AGPL",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    namespace_packages=["ckanext"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "ckan>=2.10",
    ],
    entry_points="""
        [ckan.plugins]
        search_enhanced=ckanext.search_enhanced.plugin:SearchEnhancedPlugin
    """,
)
