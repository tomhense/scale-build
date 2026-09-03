from scale_build.config import get_env_variable, get_normalized_value


CONSTRAINT_MAPPING = {
    'boolean': bool,
    'integer': int,
    'string': str,
}
DEPENDS_SCRIPT_PATH = './scripts/parse_deps.pl'


def normalize_bin_packages_depends(depends_str):
    return list(filter(lambda k: k and '$' not in k, map(str.strip, depends_str.split(','))))


def normalize_build_depends(build_depends_str):
    deps = []
    for dep in filter(bool, map(str.strip, build_depends_str.split(','))):
        for subdep in filter(bool, map(str.strip, dep.split('|'))):
            index = subdep.find('(')
            if index != -1:
                subdep = subdep[:index].strip()
            deps.append(subdep)
    return deps


def gather_build_time_dependencies(packages, deps, deps_list, visited=None):
    """Collect source packages needed to build the dependencies in ``deps_list``.

    Binary packages can share a source package, and dependency metadata can
    contain cycles.  Keep track of the binary package names already traversed
    so a cycle cannot recurse forever while still allowing each source package
    to be added to ``deps``.
    """
    visited = set() if visited is None else visited
    for dep in filter(lambda p: p in packages, deps_list):
        if dep in visited:
            continue
        visited.add(dep)
        deps.add(packages[dep].source_name)
        deps.update(gather_build_time_dependencies(
            packages,
            deps,
            packages[dep].build_dependencies | packages[dep].install_dependencies,
            visited,
        ))
    return deps


def get_normalized_specified_build_constraint_value(value_schema):
    return get_env_variable(value_schema['name'], CONSTRAINT_MAPPING[value_schema['type']])


def get_normalized_build_constraint_value(value_schema):
    return get_normalized_value(str(value_schema['value']), CONSTRAINT_MAPPING[value_schema['type']])
