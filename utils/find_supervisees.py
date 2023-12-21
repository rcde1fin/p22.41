import os

if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    from ocs_mods import browser_template  # this is an AWS layer
else:
    from ocs.browser_report import BrowserReport

# from dotenv import load_dotenv

# load_dotenv()

# query_engine_url = os.getenv("QUERY_ENGINE_URL")
# ocs_user = os.getenv("OCS_USER")
# ocs_client = os.getenv("OCS_CLIENT")
# ocs_pswd = os.getenv("OCS_PSWD")
# var_num = os.getenv("VAR_NUM")
# var_num_reload = os.getenv("VAR_NUM_RELOAD")



def findsupervisees(resno, query_engine_url, ocs_user, ocs_client, ocs_pswd, var_num):
    try:
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            client = browser_template.BrowserReport(query_engine_url, ocs_user, ocs_client, ocs_pswd)
        else:
            client = BrowserReport(query_engine_url, ocs_user, ocs_client, ocs_pswd)
        ocs_data = client.get_filtered_by_one_parm(template_id=int(var_num), parm=resno)
        print("MODULE [find_supervisees] RETRIEVED OCS DATA >>>>>>>>>>>>")
        return ocs_data
    except BaseException as e:
        print("MODULE [find_supervisees] EXCEPTION >>>>>>>>>>>>", e)
