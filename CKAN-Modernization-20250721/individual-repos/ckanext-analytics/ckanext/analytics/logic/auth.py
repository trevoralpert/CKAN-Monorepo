import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def analytics_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "analytics_get_sum": analytics_get_sum,
    }
