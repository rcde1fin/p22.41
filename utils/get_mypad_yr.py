import os

if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    from ocs_mods import browser_template  # this is an AWS layer
else:
    from ocs.browser_report import BrowserReport


def getmypadyr(query_engine_url, ocs_user, ocs_client, ocs_pswd, var_num_get_yr):
    try:
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            client = browser_template.BrowserReport(query_engine_url, ocs_user, ocs_client, ocs_pswd)
        else:
            client = BrowserReport(query_engine_url, ocs_user, ocs_client, ocs_pswd)
        mypad_yr = client.get_browser_data(template_id=int(var_num_get_yr))
        print("MODULE [get_mypad_yr] RETRIEVED myPAD YEAR >>>>>>>>>>>>", mypad_yr[0]["mp_period"])
        return mypad_yr[0]["mp_period"]
    except BaseException as e:
        print("MODULE [get_mypad_yr] EXCEPTION >>>>>>>>>>>>", e)
