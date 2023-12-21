import requests


def getresno(email, get_resno_url, get_resno_url_key):
    try:
        url = get_resno_url

        payload = {}
        headers = {
            'X-API-KEY': get_resno_url_key
        }
        response = requests.request("GET", url+email, headers=headers, data=payload)

        return response.text[0:6]
    except BaseException as e:
        print("ERROR IN GETRESNO >>>>>>>>>>>> ", e)

# import os
#
# import xmltodict
# if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
#     from ocs_mods import browser_template  # this is an AWS layer
# else:
#     from ocs.browser_report import BrowserReport
#
#
# # GETS RESNO FROM EMAIL
# def getresno(email, get_resno_url, ocs_client, ocs_user, ocs_pswd, var_num_resno):
#     try:
#         if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
#             client = browser_template.BrowserReport(wsdl=get_resno_url, username=ocs_user, client=ocs_client, password=ocs_pswd)
#         else:
#             client = BrowserReport(wsdl=get_resno_url, username=ocs_user, client=ocs_client, password=ocs_pswd)
#         resno_data = client.get_filtered_by_one_parm(template_id=int(var_num_resno), parm=email)
#         resno_parsed = xmltodict.parse(resno_data['TemplateResult'])
#         print("MODULE [get_resno] FUNCTION [getresno] SEARCHING RESNO FOR EMAIL >>>>>>>>>>>>", email)
#         if resno_parsed['Agresso']:
#             print("MODULE [get_resno] FUNCTION [getresno] RESNO FOUND >>>>>>>>>>>>", resno_parsed['Agresso']['AgressoQE']['resource_id'])
#             return resno_parsed['Agresso']['AgressoQE']['resource_id']
#         else:
#             print("MODULE [get_resno] FUNCTION [getresno] returned FALSE no RESNO found >>>>>>>>>>>>")
#             return False
#     except BaseException as e:
#         print("MODULE [get_resno] FUNCTION [getresno] EXCEPTION >>>>>>>>>>>>", e)