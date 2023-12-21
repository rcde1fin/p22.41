# based off p19-048 ocs/browser_report.py

import logging
import xmltodict
import ast
# from agresso.query_engine import QueryEngineService
from zeep.exceptions import Fault
from agresso import query_engine


class BrowserReport(object):
    def __init__(self, wsdl, username, client, password):
        self.client_service = query_engine.QueryEngineService(wsdl_url=wsdl)
        self.credentials = self.client_service.credentials(
            username=username, client=client, password=password
        )

    def about(self):
        return self.client_service.about()

    def show_all_browser_templates(self):
        result = self.client_service.get_template_list(
            form_list=None, descr_list=None, credentials=self.credentials
        )

        result_as_dict = ast.literal_eval(str(result))

        item_count = 1
        for item in result_as_dict["TemplateHeader"]:
            print("{}. {}({})".format(item_count, item["Name"], item["TemplateId"]))

            item_count += 1

    def get_browser_report(self, template_id):
        input_temp = self.client_service.input_for_template_result(
            template_id=template_id, template_filter=None, credentials=self.credentials
        )

        return self.client_service.get_template_result_as_xml(
            input_for_template_result=input_temp, credentials=self.credentials
        )["TemplateResult"]

    # taken from parser.parse_xml_no_tags2
    # promoted as a method for the BrowserReport class
    def get_browser_data(self, template_id: int) -> list:  # list of dicts
        def cook_rec(items: list) -> dict:
            row = {}
            for f in items[
                3:
            ]:  # per field or column iteration, skipping _recno, _section, and tab columns
                row.update({f[0]: f[1]})
            return row

        xml_data = self.get_browser_report(template_id)
        d = xmltodict.parse(xml_data)
        retval = []
        if "Agresso" in d.keys():
            if d["Agresso"] is not None:
                if "AgressoQE" in d["Agresso"].keys():
                    # if there are more than 1 row
                    if isinstance(d["Agresso"]["AgressoQE"], (list)):
                        # list - d['Agresso']['AgressoQE]
                        for rec in d["Agresso"][
                            "AgressoQE"
                        ]:  # per record or line iteration
                            items = list(rec.items())
                            retval.append(cook_rec(items))
                    else:
                        # only 1 row of data
                        # orderedDict - d['Agresso']['AgressoQE]
                        items = list(d["Agresso"]["AgressoQE"].items())
                        retval.append(cook_rec(items))
                else:
                    # print('no record(s)')
                    pass
            else:
                # print('NO DATA')
                pass
        else:
            # print('INVALID')
            pass

        return retval

    # based of mis-async-ocs-leaves project
    # module path: ocs/browser_report.py/get_filtered_by_email
    # refactored to be single parameter generic, omitting name of parameter - e.g. email_add
    def get_filtered_by_one_parm(self, template_id: int, parm: str):
        logger = logging.getLogger("syncApp." + __name__ + ".get_filtered_by_one_parm")

        criterias = self.client_service.get_search_criteria(
            template_id=template_id, hide_unused=False, credentials=self.credentials
        )
        criteria_list = []
        # for later: include an assertion that for the criterias list of dicts
        # only one dict will have a key whose IsParameter == True
        for x in criterias["SearchCriteriaPropertiesList"]["SearchCriteriaProperties"]:
            logger.info(f"criterias content: {x}\n")
            if x["IsParameter"]:  # changed to be more generic
                x["FromValue"] = parm

                criteria_properties = self.client_service.search_criteria_properties(
                    properties_dict=x
                )
                criteria_list.append(criteria_properties)
                exit

        temp_filter = self.client_service.array_of_search_criteria_properties(
            criteria_list
        )

        # the xml return value
        report_filter = self.client_service.input_for_template_result(
            template_id, temp_filter, credentials=self.credentials
        )

        return self.client_service.get_template_result_as_xml(
            report_filter, credentials=self.credentials
        )

    # based of mis-async-ocs-leaves project
    # module path: ocs/email_to_resno.py/get_f3_resno
    # refactored to be single parameter generic, omitting name of parameter - e.g. email_add
    def get_ocs_row(self, template_id, a_parm) -> dict:
        def cleaner(d: dict):
            # converts the complex nested ordered dict d to a flat dict

            if "Agresso" in d:
                if "AgressoQE" in d["Agresso"]:
                    tval = dict(d["Agresso"]["AgressoQE"])
            else:
                tval = {}

            if tval:
                ocs = {}
                for i in tval:
                    if i in ["_recno", "_section", "tab"]:
                        # ignore these key-value pairs
                        pass
                    else:
                        ocs[i] = tval[i]
                return ocs
            else:
                return tval

        def err_response(x, y):
            return {"errnum": x, "errmsg": y}

        # don't allow to proceed when this assertion fails!
        assert a_parm is not None, "Parameter passed is NONE!"
        try:
            raw_ocs_data = self.get_filtered_by_one_parm(template_id, a_parm)
            retval = {}
            if raw_ocs_data["ReturnCode"] == 0:
                parsed_ocs_data = xmltodict.parse(raw_ocs_data["TemplateResult"])
                # print(f'parsed_ocs_data: {parsed_ocs_data}')
                if parsed_ocs_data["Agresso"] is not None:
                    retval = cleaner(
                        parsed_ocs_data
                    )  # parsed_ocs_data["Agresso"]["AgressoQE"][:-1]
                    # if isinstance(chunk, (list)):
                    #     retval = get_leaves(chunk)
                    # retval = chunk

        except ValueError as e:
            # errnum 1
            # errmsg f"passed parameter is null/empty value \nmessage: {e}"
            return err_response(
                1, f"passed parameter is null/empty value \nmessage: {e}"
            )

        except AssertionError as e:
            # errnum 2
            # errmsg f"missing parameter(s)! \nmessage: {e}"
            return err_response(2, f"missing parameter(s)! \nmessage: {e}")

        except Fault as e:
            if e.code == "s:Server.AuthenticationError":
                return err_response(
                    10, "OCS login error on web service - check your credentials"
                )
            elif e.code == "s:Server.GeneralError":
                return err_response(
                    11, f"missing OCS browser template \nmessage: {e.message}"
                )
            else:
                return err_response(12, "ZEEP undocumented error - contact developer")

        else:
            if retval:
                # a valid dict is returned
                return retval
            else:
                # errnum 4
                # errmsg "empty set - no match found!"
                return err_response(3, "empty set - no match found!")