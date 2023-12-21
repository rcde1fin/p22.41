from zeep import Client

import ast
from agresso import zeep_plugin


class QueryEngineService(object):

    def __init__(self, wsdl_url):
        self.wsdl = wsdl_url
        self.service_client = Client(
            wsdl=self.wsdl,
            plugins=[zeep_plugin.MyLoggingPlugin()])

    def about(self):
        # operation
        return self.service_client.service.About()

    def credentials(self, username, client, password):
        cred = self.service_client.get_type('ns0:WSCredentials')

        # global type
        return cred(Username=username, Client=client,
                    Password=password)

    def get_template_list(self, form_list, descr_list, credentials):
        # operation
        return self.service_client.service.GetTemplateList(
            formList=form_list,
            descrList=descr_list,
            credentials=credentials)

    def get_search_criteria(self, template_id, hide_unused, credentials):
        # operation
        criterias = self.service_client.service.GetSearchCriteria(
            templateId=template_id,
            hideUnused=hide_unused,
            credentials=credentials)

        criterias_dict = ast.literal_eval(str(criterias))

        # debugging the browser template by param since 25 July 2020
        # print(f"criterias dict: {criterias_dict}")
        return criterias_dict

    def search_criteria_properties(self, properties_dict):
        criteria_property = self.service_client.get_type(
            'ns0:SearchCriteriaProperties')
        return criteria_property(
            ColumnName=properties_dict['ColumnName'],
            Description=properties_dict['Description'],
            RestrictionType=properties_dict['RestrictionType'],
            FromValue=properties_dict['FromValue'],
            ToValue=properties_dict['ToValue'],
            DataType=properties_dict['DataType'],
            DataLength=properties_dict['DataLength'],
            DataCase=properties_dict['DataCase'],
            IsParameter=properties_dict['IsParameter'],
            IsVisible=properties_dict['IsVisible'],
            IsPrompt=properties_dict['IsPrompt'],
            IsMandatory=properties_dict['IsMandatory'],
            CanBeOverridden=properties_dict['CanBeOverridden'],
            RelDateCrit=properties_dict['RelDateCrit'])

    def array_of_search_criteria_properties(self, array_search_criteria):
        arr_search_criteria = self.service_client.get_type(
            'ns0:ArrayOfSearchCriteriaProperties')
        return arr_search_criteria(
            SearchCriteriaProperties=array_search_criteria)

    def get_template_result_options(self, credentials):
        return self.service_client.service.GetTemplateResultOptions(
            credentials=credentials)

    def input_for_template_result(self, template_id, template_filter,
                                  credentials):
        input_for_temp = self.service_client.get_type(
            'ns0:InputForTemplateResult')

        return input_for_temp(
            TemplateId=template_id,
            TemplateResultOptions=self.get_template_result_options(
                credentials),
            SearchCriteriaPropertiesList=template_filter,
            PipelineAssociatedName=None)

    def get_template_result_as_xml(self, input_for_template_result,
                                   credentials):
        return self.service_client.service.GetTemplateResultAsXML(
            input=input_for_template_result, credentials=credentials)