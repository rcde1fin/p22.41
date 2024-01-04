# p22-41
myPAD web app

* User logs in
* Email of user captured and used to get their RESNO
* Supervisees are determined using user RESNO
* Evaluation of user if supervisor depends on supervisees returned
    - 0 supervisees -> non-supervisor
    - 1 or more supervisees -> supervisor<sup>1
* Non-supervisees redirected to non-supervisor page
* Supervisors redirected to index page

\
When supervisees are found<sup>1<br>

* Supervisees taken from OCS using supervisor RESNO as XML
* XML converted to dictionary
* Supervisees list created from dictionary and rendered in index page showing the following:
  * Smiley
  * Name
  * RESNO
  * Link to supervisee myPAD
  * Rating date
  * Rating button<sup>2<br>
* A session supervisee dataset is created and stored to a variable
* The variable containing the supervisee dataset is modified after each rating and used for subsequent index page rendering

\
When rating button is clicked<sup>2

* When rating button is clicked, user is redirected to ratestaff page
* A confirmation modal is shown when a rating is made
* If rating is confirmed, rating and rating date is written to OCS
* Supervisee data is reloaded to reflect latest changes
* User is redirected to index page containing latest supervisee data

## On deploying a stage using Zappa
Make sure to do the following prior to calling zappa deploy command for a newly-opened terminal session:
```
export AWS_PROFILE=<your AWS profile for that stage>
```

then
```
aws sso login
```

