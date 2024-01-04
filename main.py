import os
import sys
import xmltodict
import oauthlib

from flask import (
    Flask,
    render_template, request,
    redirect, url_for, session, current_app
)

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from flask_dance.contrib.google import make_google_blueprint, google

from utils.find_supervisees import findsupervisees
from utils.get_resno import getresno
from utils.patch_rating import patchrating
from utils.get_rating_date import getratingdate
from utils.get_mypad_yr import getmypadyr

from dotenv import load_dotenv

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv(override=True)


def _empty_session():
    """
    Deletes the Google token and clears the session
    """
    if "google" in current_app.blueprints and hasattr(
            current_app.blueprints['google'], "token"
    ):
        del current_app.blueprints['google'].token
    session.clear()


app = Flask(__name__)

# Global vars here
# load the environment variables that may be in AWS param store or local env file
if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
    # running in AWS
    from awsu import parmesan

    if os.environ['AWS_LAMBDA_FUNCTION_NAME'] == 'p22-41-dev':
        gest_path = "/dev/ocs/gestapo"
    elif os.environ['AWS_LAMBDA_FUNCTION_NAME'] == 'p22-41-prod':
        gest_path = "/prod/OCS/gestapo/"
    else:
        print('*** running disavowed stage... exiting')
        sys.exit(1)

    # ## AWS SSM paths by OCS general and project-specific
    parm_gestapo = parmesan.parm_recurs(
        parm_path=gest_path, with_decrypt=True
    )
    ocs_user = parmesan.parm_crawl(parm_list=parm_gestapo, parm_name="ws_user_id")
    ocs_pswd = parmesan.parm_crawl(parm_list=parm_gestapo, parm_name="ws_user_pswd")
else:
    # running in local machine
    load_dotenv(override=True)
    try:
        ocs_user = os.environ["OCS_USER"]
        ocs_pswd = os.environ["OCS_PSWD"]

    except KeyError as k:
        print(f"environment var {k} undefined")
        sys.exit(1)

try:
    # these env vars will be in AWS Lambda env vars or env file, if local
    wsdl = os.environ["QUERY_ENGINE_URL"]
    ocs_client = os.environ["OCS_CLIENT"]
    var_num = os.environ["VAR_NUM"]
    # var_num_reload = os.environ["VAR_NUM_RELOAD"]     
    var_num_resno = os.environ["VAR_NUM_RESNO"]
    app.config["SECRET_KEY"] = os.environ["APP_SECRET_KEY"]
    rest_api_employees = os.environ["REST_API_EMPLOYEE_URL"]
    var_num_get_yr = os.environ["VAR_NUM_GET_YR"]
    get_resno_url = os.environ["GET_RESNO_URL"]
    get_resno_url_key = os.environ["GET_RESNO_URL_KEY"]

except KeyError as k:
    print(f"environment var {k} undefined")
    sys.exit(1)

google_bp = make_google_blueprint(
    client_id=os.getenv("GOO_CLIENT"),
    client_secret=os.getenv("GOO_SHH"),
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    # redirect_to="landing_page",
    redirect_to="splash_screen"
)

app.register_blueprint(google_bp, url_prefix="/login")


@app.errorhandler(oauthlib.oauth2.rfc6749.errors.TokenExpiredError)
@app.errorhandler(oauthlib.oauth2.rfc6749.errors.InvalidClientIdError)
def token_expired(_):
    _empty_session()
    return redirect(url_for("landing_page"))


# TOKEN ERROR HANDLING 404 #
@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        'exception.html',
        error_title="[404] Page not found",
        error_message="The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
        mypadyr=session["mypadyr"]
    ), 404


@app.errorhandler(500)
def template_not_found(e):
    return render_template(
        'exception.html',
        error_title="[500] Template not found",
        error_message="The requested template was not found. If you entered the URL manually please check your spelling and try again.",
        mypadyr=session["mypadyr"]
    ), 500


class FormRateStaff(FlaskForm):
    staff_rating = SelectField(
        "Rating",
        validators=[DataRequired()],
        choices=[
            ('0', 'None'),
            ('12', 'Exceeded expectations'),
            ('13', 'Met expectations'),
            ('03', 'Partially Met Expectations'),
            ('14', 'Did not meet expectations')
        ],
        default='0'
    )
    submit = SubmitField("Yes")


@app.route('/help', methods=["GET", "POST"])
def help_():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template(
        'help.html',
        mypadyr=session["mypadyr"]
    )


@app.route('/ratestaff', methods=["GET", "POST"])
def rate_staff():
    if not google.authorized:
        return redirect(url_for("google.login"))

    staff_resno = request.args.get('staff_resno', None)
    staff_name = request.args.get('staff_name', None)
    staff_rating = request.args.get('staff_rating', None)

    form = FormRateStaff(staff_rating=staff_rating)
    rating = form.staff_rating.data
    # print("main.py ln 169: ", session["supervisee_data"])
    if form.validate_on_submit():
        for dict_item in session["supervisee_data"]:
            if dict_item["resource_id"] == staff_resno:
                try:
                    print("MODULE [main] FUNCTION [rate_staff] CALLING [patch_rating] FOR RESNO >>>>>>>>>>>>", staff_resno, staff_name)
                    if rating != '0':
                        res = patchrating(staff_resno, dict_item["line_no"], rating, rest_api=rest_api_employees, uname=ocs_user, pswd=ocs_pswd)
                        print("dict_item['line_no'] >>>>>>>>>>>>", dict_item["line_no"])
                    else:
                        rating = None
                        res = patchrating(staff_resno, dict_item["line_no"], rating, rest_api=rest_api_employees, uname=ocs_user, pswd=ocs_pswd)
                    print("MODULE [main] FUNCTION [rate_staff] PATCH RATING RESPONSE >>>>>>>>>>>>", res)
                except BaseException as e:
                    print("MODULE [main] FUNCTION [rate_staff] EXCEPTION >>>>>>>>>>>> ", e)

        print('MODULE [main] FUNCTION [rate_staff] MODIFYING session["supervisee_data"] IN MEMORY TO INCORPORATE RATING GIVEN')
        for item in session["supervisee_data"]:
            if item['resource_id'] == staff_resno:
                if rating is None:
                    item['rating'] = 'None'
                else:
                    item['rating'] = rating
                item['reviewdate'] = getratingdate()

        print('MODULE [main] FUNCTION [rate_staff] MODIFICATION OF session["supervisee_data"] SUCCESSFUL')
        session["supervisee_data"] = session["supervisee_data"]  # updates session["supervisee_data"] with modified version
        return redirect(url_for("landing_page"))
    return render_template(
        'ratestaff.html',
        staff_resno=staff_resno,
        staff_name=staff_name,
        form=form,
        mypadyr=session["mypadyr"]
    )


@app.route('/', methods=["GET", "POST"])
def splash_screen():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text

    session["email"] = resp.json()["email"]
    session["name"] = resp.json()["name"]
    session["picture"] = resp.json()["picture"]

    mypadyr = getmypadyr(query_engine_url=wsdl, ocs_user=ocs_user, ocs_client=ocs_client, ocs_pswd=ocs_pswd, var_num_get_yr=var_num_get_yr)
    session["mypadyr"] = mypadyr
    # session["urlyr"] = str(int(mypadyr) - 1)  # DEBUG INFO
    # print("url year: ", session["urlyr"])  # DEBUG INFO

    # Initialize reload flag to False for code block to be run once to find verify supervisor and find supervisees. Will use session data on succeeding runs.
    session["ReloadFlag"] = False

    return render_template(
        'splash.html',
        mypadyr=session["mypadyr"]
    )


@app.route('/index', methods=["GET", "POST"])
def landing_page():
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Block to be executed on first run
    if not session["ReloadFlag"]:
        session["sup_resno"] = getresno(session["email"], get_resno_url=get_resno_url, get_resno_url_key=get_resno_url_key)
        # session["sup_resno"] = getresno("d.sayo@irri.org", get_resno_url=get_resno_url, get_resno_url_key=get_resno_url_key)
        print("MODULE [main] FUNCTION [landing_page] >>>>>>>>>>>> LOGIN EMAIL: ", session["email"])
        # session["sup_resno"] = getresno(session["email"], get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)
        # session["sup_resno"] = getresno("d.sayo@irri.org", get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)
        # session["sup_resno"] = getresno("a.dejesus@irri.org", get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)
        # session["sup_resno"] = getresno("e.perez@irri.org", get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)
        # session["sup_resno"] = getresno("p.mathur@irri.org", get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)
        # session["sup_resno"] = getresno("a.kohli@irri.org", get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)
        # session["sup_resno"] = getresno("m.vandenberg@irri.org", get_resno_url=wsdl, ocs_client=ocs_client, ocs_user=ocs_user, ocs_pswd=ocs_pswd, var_num_resno=var_num_resno)

        # sets link to QlikSense URL to session data
        session["moderated_rating_url"] = os.environ["MODERATED_RATING_URL"]

        # If no RESNO is found for the email, go to non-supervisor access
        if not session["sup_resno"]:
            print("MODULE [main] FUNCTION [landing_page] >>>>>>>>>>>> NO RESNO FOUND NON-SUPERVISOR")
            return render_template(
                'nonsupervisor.html',
                name=session["name"],
                email=session["email"],
                picture=session["picture"],
                resno=session["sup_resno"],
                mypadyr=session["mypadyr"]
            )
        # If a RESNO is found, check for supervisees
        else:
            supervisee_data = findsupervisees(session["sup_resno"], query_engine_url=wsdl, ocs_user=ocs_user, ocs_client=ocs_client, ocs_pswd=ocs_pswd, var_num=var_num)
            # TemplateResult is an object in the JSON of OCS data from the find_supervisees module
            supervisees_parsed = xmltodict.parse(supervisee_data['TemplateResult'])

            # print("supervisees_parsed", supervisees_parsed)  # DEBUG INFO

            # No supervisees found. supervisees_parsed['Agresso'] contains supervisees if present, 'None' otherwise
            if not supervisees_parsed['Agresso']:
                print("MODULE [main] FUNCTION [landing_page] >>>>>>>>>>>> NON-SUPERVISOR")
                return render_template(
                    'nonsupervisor.html',
                    name=session["name"],
                    email=session["email"],
                    picture=session["picture"],
                    resno=session["sup_resno"],
                    mypadyr=session["mypadyr"]
                )
            # Supervisees found
            else:
                # print("session['ReloadFlag']:", session["ReloadFlag"])  # DEBUG INFO
                print("MODULE [main] FUNCTION [landing_page] >>>>>>>>>>>> SUPERVISOR ACCESS")
                # Initialize list
                supervisee_data = []
                # Populate list with supervisee data in dictionaries
                # print("length 1:", len(supervisees_parsed['Agresso']['AgressoQE']))  # DEBUG INFO
                # print("length 2:", len(supervisees_parsed['Agresso']))  # DEBUG INFO
                # print("type:", type(supervisees_parsed['Agresso']['AgressoQE']))  # DEBUG INFO
                if type(supervisees_parsed['Agresso']['AgressoQE']) is dict:
                    # print("Is DICT")  # DEBUG INFO
                    # print("Value:", supervisees_parsed['Agresso']['AgressoQE']['resource_id'])  # DEBUG INFO
                    supervisees = {
                        'name': supervisees_parsed['Agresso']['AgressoQE']['name'],
                        'resource_id': supervisees_parsed['Agresso']['AgressoQE']['resource_id'],
                        'rating': supervisees_parsed['Agresso']['AgressoQE']['rating'],
                        'mypadlink': supervisees_parsed['Agresso']['AgressoQE']['mypadlink'],
                        'reviewdate': supervisees_parsed['Agresso']['AgressoQE']['reviewdate'],
                        'line_no': supervisees_parsed['Agresso']['AgressoQE']['line_no'],
                        'remark': supervisees_parsed['Agresso']['AgressoQE']['remark']
                    }
                    supervisee_data.append(supervisees)
                else:
                    # print("Is LIST")  # DEBUG INFO
                    for i in range(len(supervisees_parsed['Agresso']['AgressoQE'])):
                        supervisees = {
                            'name': supervisees_parsed['Agresso']['AgressoQE'][i]['name'],
                            'resource_id': supervisees_parsed['Agresso']['AgressoQE'][i]['resource_id'],
                            'rating': supervisees_parsed['Agresso']['AgressoQE'][i]['rating'],
                            'mypadlink': supervisees_parsed['Agresso']['AgressoQE'][i]['mypadlink'],
                            'reviewdate': supervisees_parsed['Agresso']['AgressoQE'][i]['reviewdate'],
                            'line_no': supervisees_parsed['Agresso']['AgressoQE'][i]['line_no'],
                            'remark': supervisees_parsed['Agresso']['AgressoQE'][i]['remark']
                        }
                        supervisee_data.append(supervisees)
                session["supervisee_data"] = supervisee_data
                # print("SUPERVISEE DATA\n", session["supervisee_data"])  # DEBUG INFO
                session["ReloadFlag"] = True  # DEBUG CODE NOT FOR PROD
                return render_template(
                    'index.html',
                    name=session["name"],
                    email=session["email"],
                    picture=session["picture"],
                    resno=session["sup_resno"],
                    supervisee_data=session["supervisee_data"],
                    mypadyr=session["mypadyr"],
                    moderated_rating_url=session["moderated_rating_url"]
                )
    # Block to be executed on succeeding runs
    else:
        # print("Session reload flag", session["ReloadFlag"])  # DEBUG INFO
        return render_template(
            'index.html',
            name=session["name"],
            email=session["email"],
            picture=session["picture"],
            resno=session["sup_resno"],
            supervisee_data=session["supervisee_data"],
            mypadyr=session["mypadyr"],
            moderated_rating_url=session["moderated_rating_url"]
        )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5001")
